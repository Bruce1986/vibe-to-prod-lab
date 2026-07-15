"""珍奶點餐服務：呼叫 LLM → 驗契約（JSON Schema）→ 驗業務規則。

品質分層（單元一的核心觀念）：
- 第一層 JSON 解析：LLM 輸出可能根本不是 JSON。
- 第二層 契約（app/schemas/order.schema.json）：型別、枚舉、必填。
- 第三層 領域規則（validate_business_rules）：schema 表達不了的跨欄位邏輯。
"""
from __future__ import annotations

import json
from pathlib import Path

import jsonschema

from app.llm_client import LLMClient

BASE_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = BASE_DIR / "schemas" / "order.schema.json"
PROMPT_PATH = BASE_DIR / "prompts" / "order_prompt.txt"

# 領域規則常數：schema 管不到、由業務層把關
PURE_TEAS = {"冬瓜茶", "四季春茶"}  # 純茶不供應布丁
MAX_QUANTITY_PER_ITEM = 10  # 超過需門市人工確認


class OrderError(Exception):
    """點餐流程錯誤的共同基底。"""


class OrderParseError(OrderError):
    """LLM 輸出不是合法 JSON。"""


class OrderContractError(OrderError):
    """LLM 輸出違反 JSON Schema 契約。"""


class OrderRuleError(OrderError):
    """訂單違反業務規則。"""


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def validate_business_rules(order: dict) -> None:
    if order.get("status") != "ok":
        return  # need_clarification 沒有訂單內容可驗
    for item in order["items"]:
        if item["quantity"] > MAX_QUANTITY_PER_ITEM:
            raise OrderRuleError(
                f"單一品項最多 {MAX_QUANTITY_PER_ITEM} 杯"
                f"（{item['name']} 點了 {item['quantity']} 杯），請洽門市人工確認"
            )
        if item["name"] in PURE_TEAS and "布丁" in item["toppings"]:
            raise OrderRuleError(f"純茶（{item['name']}）不供應布丁配料")


def parse_order(text: str, client: LLMClient) -> dict:
    """把顧客口語訂單交給 LLM 轉結構化，並逐層驗證後回傳。"""
    raw = client.complete(load_prompt(), text)
    try:
        order = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise OrderParseError(f"LLM 輸出不是合法 JSON：{exc}") from exc
    try:
        jsonschema.validate(order, load_schema())
    except jsonschema.ValidationError as exc:
        raise OrderContractError(f"違反輸出契約：{exc.message}") from exc
    validate_business_rules(order)
    return order
