"""Golden dataset 回歸測試（lab2 的 pytest 備援軌）。

與 labs/lab2-golden-eval/ 的 promptfoo 版本共用同一批 fixtures 與同一個精神：
prompt 被改壞（拿掉關鍵約束句）時，這批測試會整排轉紅——它就是 prompt 的安全網。
"""
import json
from pathlib import Path

import pytest

from app.llm_client import FakeLLMClient
from app.service import parse_order

CASES = json.loads(
    (Path(__file__).parent / "golden_cases.json").read_text(encoding="utf-8")
)


def dig(obj, dotted_path):
    """用 "items.0.sweetness" 這種點記法往下取值。"""
    for part in dotted_path.split("."):
        obj = obj[int(part)] if part.isdigit() else obj[part]
    return obj


@pytest.mark.parametrize("case", CASES, ids=[c["input"] for c in CASES])
def test_golden(case):
    # variant="auto"：回放品質跟著 prompt 品質走，才抓得到 prompt 回歸
    order = parse_order(case["input"], FakeLLMClient())
    value = dig(order, case["field"])
    if "expect" in case:
        assert value == case["expect"]
    if "not_contains" in case:
        assert case["not_contains"] not in value
