"""單元測試＋整合測試（單元一示範）。

- 單元：直接測 validate_business_rules，不經過 LLM——快、準、可窮舉邊界。
- 整合：FakeLLMClient（回放 fixtures）＋ parse_order 全流程——驗證各層接得起來。
"""
import pytest

from app.llm_client import FakeLLMClient
from app.service import (
    OrderContractError,
    OrderParseError,
    OrderRuleError,
    parse_order,
    validate_business_rules,
)


def make_order(**overrides):
    """組一筆合法訂單，讓每個測試只寫出它在乎的欄位。"""
    item = {
        "name": "珍珠奶茶",
        "size": "M",
        "sweetness": 50,
        "ice": "少冰",
        "toppings": [],
        "quantity": 1,
    }
    item.update(overrides)
    return {"status": "ok", "items": [item]}


class TestBusinessRulesUnit:
    def test_normal_order_passes(self):
        validate_business_rules(make_order())  # 不丟例外即通過

    def test_quantity_at_limit_passes(self):
        validate_business_rules(make_order(quantity=10))

    def test_quantity_over_limit_rejected(self):
        with pytest.raises(OrderRuleError, match="10"):
            validate_business_rules(make_order(quantity=11))

    def test_pure_tea_with_pudding_rejected(self):
        with pytest.raises(OrderRuleError, match="布丁"):
            validate_business_rules(make_order(name="冬瓜茶", toppings=["布丁"]))

    def test_need_clarification_skips_rules(self):
        validate_business_rules({"status": "need_clarification", "question": "想喝什麼？"})


class TestParseOrderIntegration:
    def test_happy_path(self):
        order = parse_order("我要一杯大杯珍珠奶茶，半糖少冰", FakeLLMClient())
        assert order["status"] == "ok"
        assert order["items"][0]["size"] == "L"
        assert order["items"][0]["sweetness"] == 50

    def test_ambiguous_input_asks_back(self):
        order = parse_order("來點好喝的", FakeLLMClient())
        assert order["status"] == "need_clarification"
        assert "question" in order

    def test_contract_catches_hallucinated_topping(self):
        # 強制回放 sloppy：模擬 LLM 幻覺出菜單上沒有的配料，契約層要接住
        client = FakeLLMClient(variant="sloppy")
        with pytest.raises(OrderContractError):
            parse_order("一杯大杯珍珠奶茶全糖去冰，加跳跳糖", client)

    def test_parse_error_on_malformed_json(self):
        # 強制回放 sloppy：模擬 LLM 輸出被截斷的壞 JSON
        client = FakeLLMClient(variant="sloppy")
        with pytest.raises(OrderParseError):
            parse_order("一杯芋頭鮮奶微糖微冰", client)
