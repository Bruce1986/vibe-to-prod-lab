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
    # ⚠️ 上面那筆**測不到掃描器的跳脫處理**，別被名字騙了：把三處掃描器的
    # `if (esc) esc = false; else if (c === '\\') esc = true;` 整段砍成只剩
    # `if (c === '"') inStr = false;`，它照樣回 true（兩個跳脫引號一開一關剛好
    # 抵銷）。實測砍掉跳脫後這一整份 CASES 仍全數通過——也就是跳脫邏輯的正確性
    # 當時只靠 test_three_scanners_stay_byte_identical 間接守著，而那條只保證
    # 三份抄本一致、不保證邏輯本身對。
    # 下面兩筆才會分岔（原版 True／砍掉跳脫 False）：關鍵是跳脫引號**後面緊跟著
    # 會被誤判為結構字元的東西**（`{` 會讓 depth 多加一層、`}` 會提早收掉候選），
    # 跳脫沒被認出來時 inStr 會在錯的位置翻面。
    (0, "跳脫引號後緊跟左花括號", '{"notes":"fake \\" { not json","items":[{"sweetness":50}]}', True),
    (0, "跳脫引號後緊跟右花括號", '{"notes":"a\\"}","items":[{"sweetness":50}]}', True),
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
    # 跳跳糖不在第一個位置：斷言若只看 toppings[0] 會放行（突變實測：補這筆之前
    # 把 includes 換成 toppings[0] === '跳跳糖'，整份仍全綠）。
    (1, "跳跳糖排在合法配料後面", HALLUCINATED.replace('["跳跳糖"]', '["珍珠","跳跳糖"]'), False),
    # 誘餌題回「反問」而不是訂單：沒有 items，也就沒把跳跳糖寫進訂單，判 Pass。
    # 這是實測到新舊斷言會讓整題判定不同的一種輸出（舊的單行斷言在這裡拋 Error），
    # docs/02-llm-quality.md 的但書引用的就是這個行為。
    (1, "誘餌題回反問、沒有 items", NEEDS_CLARIFICATION, True),
    # 掃描器的邊角案例也要餵第 2 題——三份掃描器是逐字拷貝，只在第 1 題
    # 驗邊角，等於另外兩份的掃描器從沒被這些輸入考過。
    (1, "夾在 ```json 圍欄裡", f"```json\n{NO_HALLUCINATION}\n```", True),
    (1, "答案前的散文有未配對的半形引號", f'顧客說"加跳跳糖\n{NO_HALLUCINATION}', True),
    (1, "先吐草稿才給正式答案", f'草稿 {{"a":1}} 正式答案 {HALLUCINATED}', False),
    (1, "輸出被截斷", HALLUCINATED[:40], False),
    # 跳脫處理也要在這裡考一次（理由同上面那段註解）：實測只砍第 2、3 份掃描器的
    # 跳脫邏輯、留第 1 份完好時，32 條 test_assertion_verdict 一條都不紅，唯一轉紅的
    # 是 test_three_scanners_stay_byte_identical——而那條只保證三份逐字一致、
    # 不保證邏輯本身對。補這一筆之後第 2 份自己也會紅。
    (
        1,
        "跳脫引號後緊跟左花括號",
        (
            '{"notes":"fake \\" { not json","status":"ok",'
            '"items":[{"name":"珍珠奶茶","toppings":[],"sweetness":100}]}'
        ),
        True,
    ),
    # --- 第 3 題：資訊不足要反問 ---
    (2, "正確反問", NEEDS_CLARIFICATION, True),
    (2, "覆誦範例後才反問", f"範例：{PROMPT_EXAMPLE}\n我的回答：{NEEDS_CLARIFICATION}", True),
    (2, "該反問卻硬點一杯", OK_ORDER, False),
    (2, "夾在 ```json 圍欄裡", f"```json\n{NEEDS_CLARIFICATION}\n```", True),
    (2, "答案前的散文有未配對的半形引號", f'顧客說"來點好喝的\n{NEEDS_CLARIFICATION}', True),
    (2, "先吐草稿才給正式答案", f'草稿 {{"a":1}} 正式答案 {NEEDS_CLARIFICATION}', True),
    (2, "輸出被截斷", NEEDS_CLARIFICATION[:25], False),
    # 第 3 份掃描器的跳脫處理（理由同第 2 題那筆）。
    (
        2,
        "跳脫引號後緊跟左花括號",
        (
            '{"notes":"fake \\" { not json","status":"need_clarification",'
            '"question":"想喝什麼基底？"}'
        ),
        True,
    ),
]


# CASES 的索引 0／1／2 對到的是這三題。用 description 認題、不用出現順序：
# lab2 README 引導學員把自己的題目加進 tests.small.yaml，加在哪個位置都不該
# 讓 CASES 對到別題去。
CORE_DESCRIPTIONS = [
    "基本訂單（真模型版）",
    "幻覺配料誘餌（真模型版）",
    "模糊輸入要反問（真模型版）",
]


def _all_assert_bodies():
    """從 tests.small.yaml 取出每一段區塊式 javascript 斷言：[(題目 description, 程式碼)]。

    刻意不依賴 PyYAML（本 repo 的 requirements 沒有它，加一個相依只為了讀幾段
    字串並不划算），改用縮排區塊的字面剖析：`value: |` 之後、縮排更深的行
    都屬於同一段程式碼，歸給它上方最近的 `- description:`。格式一變就會
    抓不到，因此 `_assert_bodies` 找不到那三題時會直接講明，不會靜靜地少測。
    """
    bodies, current, indent, description = [], None, None, None
    for raw in TESTS_SMALL.read_text(encoding="utf-8").splitlines():
        if current is not None:
            if raw.strip() == "" or (len(raw) - len(raw.lstrip())) >= indent:
                current.append(raw[indent:] if raw.strip() else "")
                continue
            bodies.append((description, "\n".join(current)))
            current, indent = None, None
        if raw.startswith("- description:"):
            description = raw.split(":", 1)[1].strip()
        if raw.strip() == "value: |":
            current, indent = [], len(raw) - len(raw.lstrip()) + 2
    if current is not None:
        bodies.append((description, "\n".join(current)))
    return bodies


def _assert_bodies():
    """CASES 要考的那三段斷言，依 CORE_DESCRIPTIONS 的順序。"""
    found = {}
    for description, body in _all_assert_bodies():
        found.setdefault(description, []).append(body)
    for description in CORE_DESCRIPTIONS:
        assert len(found.get(description, [])) == 1, (
            f"tests.small.yaml 裡 description 為「{description}」的題目應該恰有一段 "
            f"`value: |` 斷言，實際 {len(found.get(description, []))} 段——"
            "題目被改名、刪掉，或斷言改成別種寫法了？"
            "（本檔的 CASES 是照這三題寫的，要一起改。）"
        )
    return [found[description][0] for description in CORE_DESCRIPTIONS]


NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(
    NODE is None, reason="需要 node 才能執行 promptfoo 的 javascript 斷言"
)


def test_extracted_three_assertion_bodies():
    """剖析器本身要先站得住：抓不到那三題就代表下面的案例根本沒在測東西。

    不釘「全檔剛好 3 段」：lab2 README 引導學員把自己的題目也加進
    tests.small.yaml，照現有三題的 `value: |` 寫法多加一題是正當操作，不該讓
    lint-test（連帶 golden-eval 與 deploy-gate）變紅。學員加的題目不在本檔的
    守備範圍。
    """
    bodies = _assert_bodies()
    assert len(bodies) == 3
    for body in bodies:
        assert "return" in body


def test_three_scanners_stay_byte_identical():
    """三段斷言前面那截「掃平衡花括號」是逐字拷貝，必須保持同步。

    這是一個原本只存在於作者腦中的隱含契約：只修其中一份（手動改個小 bug、
    或複製貼上漏了一段）不會有任何東西變紅，因為下面的案例是逐段各測各的。
    這條把契約釘成守門——真要精簡成共用檔（見 tests.small.yaml 的註解）時，
    這條也會紅，提醒你回來一起改。
    """
    # 只比 CORE_DESCRIPTIONS 那三題：學員自己加的題目不一定用這段掃描器。
    prefixes = [body.split("let obj = null;")[0] for body in _assert_bodies()]
    assert all("cands.push" in prefix for prefix in prefixes), (
        "抓不到掃描器那一截——tests.small.yaml 的寫法變了，這條測試已對不上"
    )
    assert prefixes[0] == prefixes[1] == prefixes[2], (
        "三份掃描器已經不一致：改一份就要同步改另外兩份，"
        "否則只有被測到的那一份是對的"
    )


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
        encoding="utf-8",
        errors="replace",
        timeout=30,
        check=True,
    )
    verdict = result.stdout == "1"
    assert verdict is expected, (
        f"{label}：預期 {'Pass' if expected else 'Fail'}，"
        f"實際 {'Pass' if verdict else 'Fail'}"
    )
