"""契約測試：JSON Schema 是 LLM 輸出的守門員。

兩個方向都要驗：
1. 所有 good fixtures 必須通過 schema（契約不能誤殺正常輸出）。
2. 已知的 sloppy 樣本必須被 schema 擋下（契約抓得住幻覺與型別錯誤）。
"""
import json

import jsonschema
import pytest

from app.llm_client import FIXTURES_PATH
from app.service import load_schema

FIXTURES = json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))
CASE_KEYS = [k for k in FIXTURES if not k.startswith("__")]

# 這四筆的 sloppy 變體是「schema 抓得到」的錯誤型態：
# 甜度型別錯、數量型別錯、冰塊枚舉外、幻覺配料
SCHEMA_INVALID_SLOPPY = [
    "我要一杯大杯珍珠奶茶，半糖少冰",
    "兩杯中杯紅茶拿鐵，全糖正常冰，加波霸",
    "一杯熱的紅茶拿鐵，微冰",
    "一杯大杯珍珠奶茶全糖去冰，加跳跳糖",
]


@pytest.mark.parametrize("user_input", CASE_KEYS)
def test_good_variants_satisfy_contract(user_input):
    jsonschema.validate(FIXTURES[user_input]["good"], load_schema())  # 不丟例外即通過


@pytest.mark.parametrize("user_input", SCHEMA_INVALID_SLOPPY)
def test_known_sloppy_variants_violate_contract(user_input):
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(FIXTURES[user_input]["sloppy"], load_schema())
