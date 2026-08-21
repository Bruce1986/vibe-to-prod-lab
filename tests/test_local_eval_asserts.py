"""加分關（eval-local）語意斷言的守門測試。

為什麼需要這一份：`tests.small.yaml` 的三條斷言是內嵌在 YAML 裡的 JavaScript，
promptfoo 只有在真的跑一次評測（要有 Ollama、要拉模型）時才會執行它們，
本機與 lint-test 這一關都不會碰到。斷言自己寫錯時沒有任何守門會紅，
而它算出來的 1/3 這種分數又被四份教材當證據引用——所以斷言本身也要被測。

這裡刻意**讀取 tests.small.yaml 裡真正在跑的那段程式碼**再交給 node 執行，
而不是在測試裡另抄一份實作。抄一份只能證明兩份副本一致（差分測試的假守門），
證明不了線上那份是對的。
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TESTS_SMALL = REPO_ROOT / "labs" / "lab2-golden-eval" / "tests.small.yaml"

# 一份合法、且甜度＝50（第一題的正解）的訂單 JSON。
OK_ORDER = '{"status":"ok","items":[{"name":"珍珠奶茶","size":"L","sweetness":50,"ice":"少冰","toppings":[],"quantity":1}]}'
# order_prompt.txt 裡內嵌的格式範例之一——小模型很常整段覆誦。
PROMPT_EXAMPLE = '{"status": "need_clarification", "question": "..."}'
HALLUCINATED = '{"status":"ok","items":[{"name":"珍珠奶茶","toppings":["跳跳糖"],"sweetness":100}]}'
NO_HALLUCINATION = '{"status":"ok","items":[{"name":"珍珠奶茶","toppings":[],"sweetness":100}]}'
NEEDS_CLARIFICATION = '{"status":"need_clarification","question":"想喝什麼基底？"}'

# (斷言索引, 說明, 模型輸出, 期望判定)
# True＝該筆應該 Pass；False＝該筆應該 Fail。
CASES = [
    # --- 第 1 題：甜度要映射成 50 ---
    (0, "乾淨的單一 JSON", OK_ORDER, True),
    (0, "夾在 ```json 圍欄裡", f"```json\n{OK_ORDER}\n```", True),
    (0, "先覆誦格式範例才給答案", f"格式：{PROMPT_EXAMPLE}\n我的回答：\n{OK_ORDER}", True),
    (0, "先吐草稿才給正式答案", f'草稿 {{"a":1}} 正式答案 {OK_ORDER}', True),
    (0, "答案前的散文有未配對的半形引號", f'顧客說"來點好喝的\n{OK_ORDER}', True),
    (0, "字串內含跳脫引號", '{"notes":"他說\\"半糖\\"","items":[{"sweetness":50}]}', True),
    (0, "字串內含未配對花括號", '{"notes":"符號 {","items":[{"sweetness":50}]}', True),
    (0, "巢狀物件", '{"a":{"b":{"c":1}},"items":[{"sweetness":50}]}', True),
    # 以下是真的答錯／讀不出訂單，必須維持 Fail
    (0, "甜度答錯成 100", OK_ORDER.replace('"sweetness":50', '"sweetness":100'), False),
    (0, "輸出被截斷", OK_ORDER[:40], False),
    (0, "完全不是 JSON", "好的，一杯半糖少冰的大珍奶！", False),
    (0, "空輸出", "", False),
    (0, "items 是空陣列", '{"status":"ok","items":[]}', False),
    (0, "只有頂層陣列、沒有物件", '[{"sweetness":50}]', False),
    # --- 第 2 題：不得把幻覺配料寫進訂單 ---
    (1, "把跳跳糖寫進 toppings", HALLUCINATED, False),
    (1, "覆誦範例後仍寫進跳跳糖", f"格式：{PROMPT_EXAMPLE}\n{HALLUCINATED}", False),
    (1, "正確忽略跳跳糖", NO_HALLUCINATION, True),
    (1, "格式壞到讀不出訂單", "抱歉，我不會做跳跳糖珍奶", False),
    # --- 第 3 題：資訊不足要反問 ---
    (2, "正確反問", NEEDS_CLARIFICATION, True),
    (2, "覆誦範例後才反問", f"範例：{PROMPT_EXAMPLE}\n我的回答：{NEEDS_CLARIFICATION}", True),
    (2, "該反問卻硬點一杯", OK_ORDER, False),
]


def _assert_bodies():
    """從 tests.small.yaml 取出三條 javascript 斷言的原始程式碼。

    刻意不依賴 PyYAML（本 repo 的 requirements 沒有它，加一個相依只為了讀三段
    字串並不划算），改用縮排區塊的字面剖析：`value: |` 之後、縮排更深的行
    都屬於同一段程式碼。格式一變就會抓不到，因此下面有一條測試專門盯著
    「確實抓到 3 段」，抓錯不會靜靜地少測。
    """
    bodies, current, indent = [], None, None
    for raw in TESTS_SMALL.read_text(encoding="utf-8").splitlines():
        if current is not None:
            if raw.strip() == "" or (len(raw) - len(raw.lstrip())) >= indent:
                current.append(raw[indent:] if raw.strip() else "")
                continue
            bodies.append("\n".join(current))
            current, indent = None, None
        if raw.strip() == "value: |":
            current, indent = [], len(raw) - len(raw.lstrip()) + 2
    if current is not None:
        bodies.append("\n".join(current))
    return bodies


NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(
    NODE is None, reason="需要 node 才能執行 promptfoo 的 javascript 斷言"
)


def test_extracted_three_assertion_bodies():
    """剖析器本身要先站得住：抓不到 3 段就代表下面的案例根本沒在測東西。"""
    bodies = _assert_bodies()
    assert len(bodies) == 3, f"預期從 tests.small.yaml 取出 3 段斷言，實際 {len(bodies)} 段"
    for body in bodies:
        assert "return" in body


@pytest.mark.parametrize(
    ("index", "label", "output", "expected"),
    CASES,
    ids=[f"{i}-{label}" for i, label, _, _ in CASES],
)
def test_assertion_verdict(index, label, output, expected):
    """把真正在跑的斷言碼餵給 node，確認它對每種模型輸出的判定符合預期。"""
    body = _assert_bodies()[index]
    script = (
        "const body = JSON.parse(process.argv[1]);"
        "const output = JSON.parse(process.argv[2]);"
        "let verdict;"
        "try { verdict = new Function('output', body)(output) === true; }"
        "catch (e) { verdict = false; }"
        "process.stdout.write(verdict ? '1' : '0');"
    )
    result = subprocess.run(
        [NODE, "-e", script, json.dumps(body), json.dumps(output)],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    verdict = result.stdout == "1"
    assert verdict is expected, (
        f"{label}：預期 {'Pass' if expected else 'Fail'}，"
        f"實際 {'Pass' if verdict else 'Fail'}"
    )
