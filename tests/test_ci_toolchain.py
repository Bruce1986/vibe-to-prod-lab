"""CI 的工具鏈前提：node 不在，就不是「全綠」而是「什麼都沒測」。

`tests/test_eval_summary.py` 與 `tests/test_local_eval_asserts.py` 這兩份，
每一條都要真的叫 node 跑「線上那份」JavaScript（tests.small.yaml 的斷言、
summarize_eval.js 的判讀）。兩份都用 `skipif(node 不在)` 保護，本機沒裝 node
的人才跑得動 pytest——代價是**沒有 node 時它們整批靜默跳過、pytest 仍 exit 0**。
本機實測：`env -i PATH=<空目錄> pytest tests/test_eval_summary.py
tests/test_local_eval_asserts.py` → 全部 skipped、離開碼 0。

CI 上那正是最糟的失效：守門一條都沒跑，儀表板卻是綠的。所以在 CI 上把
「沒有 node」變成紅燈；本機維持可跳過。

刻意不在任何地方寫死「共幾條」：這個數字每次增修 parametrize 就會變，
寫死等於留一句遲早過期的宣稱（本檔第一版就寫了 35，當下實際是 38）。
"""

import os
import re
import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
QUALITY_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "quality.yml"
IN_CI = os.environ.get("CI", "").lower() in {"1", "true", "yes"}


def test_lint_test_job_installs_node():
    """跑 pytest 的那個 job 必須自己裝 node，不能賭 runner 映像剛好有。

    這條才是真正擋得住回歸的那道：下面 `which("node")` 只看執行當下的 PATH，
    有人把 setup-node 從 quality.yml 拿掉、而 runner 剛好預裝 node 時，它照樣
    綠——於是「兩份 node 測試會不會跑」又變回沒有人保證的事。
    """
    workflow = QUALITY_WORKFLOW.read_text(encoding="utf-8")
    lint_test = workflow.split("  lint-test:", 1)
    assert len(lint_test) == 2, "找不到 lint-test job——這條測試已對不上 quality.yml"
    # 只看到下一個 job 為止，免得誤採 golden-eval 的 setup-node
    body = re.split(r"\n  \w[\w-]*:\n", lint_test[1])[0]
    # 比對 `uses:` 欄位而不是整段文字裡「有沒有出現這串字」：純子串比對會被
    # step 名稱或註解裡的同一串字騙過去。實測把 setup-node 換成 apt-get 裝 node、
    # 但 step 取名為「安裝 Node（改用 apt，不再用 actions/setup-node）」時，
    # 子串版本會誤判通過（1 passed），而這個版本會正確轉紅。
    #
    # **先丟掉整行註解再比對**：只換成 `uses:` 正則是不夠的——拿掉 action 時最
    # 自然的寫法就是把原本那行 `uses: actions/setup-node@v4` 註解掉留著，那樣
    # 正則照樣命中、照樣假綠（實測：改 apt ＋ 註解保留整行 → 1 passed）。
    # **引號要放行**：`uses: "actions/setup-node@v4"` 與單引號版都是合法 YAML，
    # 不加引號分支會把它們判成紅（實測兩種各 1 failed），那是舊子串版本本來就過的。
    # 已知限制：本地 composite wrapper（`uses: ./.github/actions/setup-node`）
    # 仍抓不到——要正確處理得真的解析 YAML，而 PyYAML 不在 requirements.txt 裡。
    lines = [ln for ln in body.splitlines() if not ln.lstrip().startswith("#")]
    assert re.search(
        r"""uses:\s*["']?actions/setup-node(?:[@"']|\s|$)""", "\n".join(lines)
    ), (
        "lint-test 沒有以 `uses: actions/setup-node` 裝 node："
        "tests/test_eval_summary.py 與 tests/test_local_eval_asserts.py "
        "會被整批靜默跳過，pytest 仍會全綠"
    )

def test_all_workflows_pin_the_same_node_version():
    """「各軌一致」就要真的掃過各軌，不能只掃 quality.yml。

    這條原本併在上面那個函式裡，`re.findall` 的對象是 quality.yml 的內文，
    斷言訊息卻寫「各軌的 node 版本應該一致」——實際只比對了 quality.yml 內部
    lint-test 與 golden-eval 兩個 job。`eval-local.yml`（學員按 `/local-eval`
    走的那一軌）自己也釘 node 版本，漂移完全沒有人管：實測把 eval-local.yml
    改成 `node-version: 20`、其餘不動，整份 pytest 仍全綠。

    改成掃 `.github/workflows/` 底下**所有**釘了 node-version 的檔案，新增
    workflow 會自動納入，不必回來改這條。突變實證：eval-local.yml 改 20 →
    紅；slides.yml 改 18 → 紅；把 glob 指到不存在的目錄 → 紅（即這條不是
    恆真，掃不到東西也會講）。
    """
    per_file = {}
    for path in sorted((REPO_ROOT / ".github" / "workflows").glob("*.yml")):
        found = re.findall(
            r"node-version:\s*[\"']?(\d+)", path.read_text(encoding="utf-8")
        )
        if found:
            per_file[path.name] = sorted(set(found))
    assert per_file, "沒有任何 workflow 釘 node-version——這條測試已對不上 repo"
    versions = {v for vs in per_file.values() for v in vs}
    assert len(versions) == 1, (
        f"各軌的 node 版本應該一致，目前有 {sorted(versions)}：{per_file}"
    )


@pytest.mark.skipif(not IN_CI, reason="本機允許沒有 node（那兩份會整批跳過）；CI 上不允許")
def test_node_is_available_in_ci():
    assert shutil.which("node"), (
        "CI 上找不到 node：tests/test_eval_summary.py 與 "
        "tests/test_local_eval_asserts.py 會被整批靜默跳過，pytest 仍會全綠。"
        "請確認 workflow 裡有 actions/setup-node。"
    )
