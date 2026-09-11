"""加分關（eval-local）結果判讀的守門測試。

為什麼需要這一份：`summarize_eval.js` 印出來的那段話，是讀者對這次評測唯一
會看到的結論。它只有在 CI 上真的跑完一次 eval-local（要 Ollama、要拉模型、
要好幾分鐘 CPU 推論）才會被執行，判讀寫錯時沒有任何守門會紅——而寫錯的
代價正是它要防的那件事：把「模型根本沒作答」印成「小模型答錯」。

這裡跑的是 `labs/lab2-golden-eval/summarize_eval.js` 本尊（不另抄一份實作），
餵的是 `tests/fixtures/eval_local/` 底下 promptfoo 實跑出來的原始 output.json
（產生方式見該目錄的 README）。兩側都要驗：壞掉時會不會紅、正常時會不會綠。
只驗一側的守門會被「永遠說未完成」這種壞修法騙過去。
"""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SUMMARIZER = REPO_ROOT / "labs" / "lab2-golden-eval" / "summarize_eval.js"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "eval_local"
PROVIDER_ERROR = FIXTURES / "output_provider_error.json"
ANSWERED = FIXTURES / "output_answered.json"

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="需要 node 才能執行 summarize_eval.js")

INCOMPLETE_HEADING = "eval-local 未完成"
COMPLETE_HEADING = "eval-local 完成"


def run_summary(output_path, model="qwen2.5:1.5b", cwd=None):
    """跑真正的 summarize_eval.js，回傳它印出來的 markdown。

    刻意不用 `check=True`：CalledProcessError 的訊息只有「exit status 1」，
    node 真正丟的 TypeError／stack trace 留在 capture 起來的 stderr 裡不會被
    印出來。這支程式崩掉正是本檔要守的事故之一（崩掉＝step summary 一片空白），
    守門自己紅的時候得看得出原因。
    """
    result = subprocess.run(
        [NODE, str(SUMMARIZER), str(output_path)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
        cwd=str(cwd or REPO_ROOT),
        env={"PATH": os.environ.get("PATH", ""), "MODEL": model},
    )
    assert result.returncode == 0, (
        f"summarize_eval.js 以 {result.returncode} 結束——它應該永遠印得出東西。\n"
        f"stderr:\n{result.stderr}"
    )
    return result.stdout


# --- 先確認 fixture 本身還是我們以為的那個形狀 -------------------------------
# 這幾條看起來像在測資料，但它們守的是「下面那些測試有沒有在測空氣」：
# promptfoo 換版把欄位改名時，若沒有這幾條，判讀測試會因為「反正也讀不到
# 輸出」而繼續全綠，實際上什麼都沒驗到。


def test_provider_error_fixture_shape():
    """壞掉那份的關鍵前提：合法 JSON、有結果列、輸出全空、errors 卻是 0。"""
    data = json.loads(PROVIDER_ERROR.read_text(encoding="utf-8"))
    rows = data["results"]["results"]
    assert len(rows) == 3
    assert all(row["response"]["output"] == "" for row in rows), "fixture 應該每一題都沒有輸出"
    assert data["results"]["stats"]["errors"] == 0, (
        "這份 fixture 的重點就是 errors=0——若 promptfoo 改成會記 error，"
        "『找 ERROR 列』就變成可行的判讀方式，這條測試提醒你回去重新評估"
    )


def test_answered_fixture_shape():
    """正常那份的關鍵前提：每一題都有非空輸出，而且全部通過。"""
    data = json.loads(ANSWERED.read_text(encoding="utf-8"))
    rows = data["results"]["results"]
    assert len(rows) == 3
    assert all(row["response"]["output"].strip() for row in rows)
    assert sum(1 for row in rows if row["success"]) == 3


# --- 判讀本身：紅的那一側 ----------------------------------------------------


def test_provider_error_is_not_reported_as_model_quality():
    """模型沒作答時，摘要必須說『未完成』，而且不能宣告完成或報成績。"""
    summary = run_summary(PROVIDER_ERROR)
    assert INCOMPLETE_HEADING in summary
    assert COMPLETE_HEADING not in summary
    assert "本次成績" not in summary
    assert "不要" in summary


def test_missing_output_file_is_reported_as_runtime_error():
    summary = run_summary(FIXTURES / "does-not-exist.json")
    assert INCOMPLETE_HEADING in summary
    assert COMPLETE_HEADING not in summary


@pytest.mark.parametrize(
    ("label", "content"),
    [
        ("空檔", ""),
        ("不是 JSON", "promptfoo crashed"),
        ("沒有 results 陣列", '{"results": {"stats": {}}}'),
        ("一筆結果都沒有", '{"results": {"results": [], "stats": {}}}'),
        ("結果列是 null", '{"results": {"results": [null], "stats": {}}}'),
        ("結果列是字串", '{"results": {"results": ["oops"], "stats": {}}}'),
        # 這一筆才真的會走到算分那段：前一列有作答，answered 數 > 0，
        # 於是 rows.filter(row => row.success) 會碰到 null。上面兩筆在
        # 「全部沒作答」就先轉彎了，測不到崩潰路徑（突變實測確認過）。
        (
            "有作答的列後面混一個 null",
            json.dumps(
                {
                    "results": {
                        "results": [
                            {"response": {"output": '{"status":"ok"}'}, "success": True},
                            None,
                        ],
                        "stats": {"errors": 0},
                    }
                }
            ),
        ),
    ],
)
def test_unusable_output_files_are_runtime_errors(tmp_path, label, content):
    broken = tmp_path / "output.json"
    broken.write_text(content, encoding="utf-8")
    summary = run_summary(broken)
    assert INCOMPLETE_HEADING in summary, f"{label} 應判為執行期錯誤"
    assert COMPLETE_HEADING not in summary, f"{label} 不該被宣告完成"


# --- 判讀本身：綠的那一側 ----------------------------------------------------


def test_answered_run_is_reported_complete_with_real_score():
    """真的有作答時要說『完成』，並報出這次實際的分數，而不是只複述歷史對照。"""
    summary = run_summary(ANSWERED)
    assert COMPLETE_HEADING in summary
    assert INCOMPLETE_HEADING not in summary
    assert "本次成績：3/3" in summary
    assert "qwen2.5:1.5b" in summary


def test_score_reflects_actual_failures(tmp_path):
    """分數要跟著結果走：把其中一題改成失敗，摘要就得報 2/3。

    這條是拿來釘死『成績是算出來的、不是寫死的』——直接印一句固定的 3/3
    也能讓上面那條過。
    """
    data = json.loads(ANSWERED.read_text(encoding="utf-8"))
    data["results"]["results"][0]["success"] = False
    downgraded = tmp_path / "output.json"
    downgraded.write_text(json.dumps(data), encoding="utf-8")
    summary = run_summary(downgraded)
    assert "本次成績：2/3" in summary
    assert COMPLETE_HEADING in summary


def test_partial_no_answer_run_is_flagged(tmp_path):
    """只有部分題目沒拿到輸出時，仍算完成，但要標出那幾題的紅不是答錯。"""
    data = json.loads(ANSWERED.read_text(encoding="utf-8"))
    data["results"]["results"][0]["response"]["output"] = ""
    data["results"]["results"][0]["success"] = False
    partial = tmp_path / "output.json"
    partial.write_text(json.dumps(data), encoding="utf-8")
    summary = run_summary(partial)
    assert COMPLETE_HEADING in summary
    assert "1 題沒有拿到任何模型輸出" in summary


# --- workflow 真的有在用這支程式嗎 -------------------------------------------


WORKFLOW = REPO_ROOT / ".github" / "workflows" / "eval-local.yml"


def test_workflow_calls_the_summarizer():
    """判讀再準，workflow 沒呼叫它也是白搭（這正是它上一版的失效方式）。"""
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "node summarize_eval.js output.json" in workflow
    assert "working-directory: labs/lab2-golden-eval" in workflow


def test_eval_is_time_boxed_inside_its_step():
    """評測要自己控時，而且要留得下寫摘要的時間。

    step 層的 timeout-minutes 先觸發時 GitHub 會砍掉整個 run block，判讀與
    step summary 一行都不會執行——本檔在 job 層特別防的就是這件事，這一步
    才是最可能吃滿時間的那層。所以 `timeout N` 必須存在、且嚴格小於本步驟的
    timeout-minutes（留給判讀的餘裕）。
    """
    workflow = WORKFLOW.read_text(encoding="utf-8")
    seconds = re.search(r"^\s*timeout (\d+) npx .*promptfoo.* eval\b", workflow, re.MULTILINE)
    assert seconds, "評測指令必須用 `timeout <秒> npx … promptfoo … eval` 自己控時"

    step = workflow.split("- name: 本地模型評測", 1)
    assert len(step) == 2, "找不到『本地模型評測』這個 step——測試已對不上 workflow"
    step_minutes = re.search(r"^\s*timeout-minutes:\s*(\d+)", step[1], re.MULTILINE)
    assert step_minutes, "『本地模型評測』step 應保留 timeout-minutes 當第二道保險"
    assert int(seconds.group(1)) < int(step_minutes.group(1)) * 60, (
        f"自控 timeout {seconds.group(1)}s 沒有小於 step 的 "
        f"{step_minutes.group(1)} 分鐘，摘要仍會被 GitHub 砍掉"
    )
