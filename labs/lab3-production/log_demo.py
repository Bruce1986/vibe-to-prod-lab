"""產生一份 LLM 呼叫的結構化 log（JSONL），欄位對齊 OTel gen_ai.* 慣例。

執行：python labs/lab3-production/log_demo.py
輸出：repo 根目錄 llm_calls.jsonl（執行產物，已列入 .gitignore）
"""
from __future__ import annotations

import json
import sys
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))  # 讓本腳本可直接執行，不必透過 pytest

from app.llm_client import FakeLLMClient  # noqa: E402
from app.service import load_prompt, parse_order  # noqa: E402

INPUTS = [
    "我要一杯大杯珍珠奶茶，半糖少冰",
    "三杯冬瓜茶無糖去冰",
    "來點好喝的",
]

# 示範單價（美元／1K tokens）；真實值依所用模型的定價表
PRICE_PER_1K_INPUT = 0.00015
PRICE_PER_1K_OUTPUT = 0.0006


def fake_token_count(text: str) -> int:
    """教學用粗估：CJK 大約 1 字 ≒ 0.5 token 的反向近似，重點是欄位語意不是精度。"""
    return max(1, len(text) // 2)


def main() -> None:
    client = FakeLLMClient()
    out_path = ROOT / "llm_calls.jsonl"
    trace_id = uuid.uuid4().hex  # 同一批對話共用一條 trace
    with out_path.open("w", encoding="utf-8") as f:
        for i, text in enumerate(INPUTS):
            start = time.perf_counter()
            order = parse_order(text, client)
            latency_ms = round((time.perf_counter() - start) * 1000, 2)

            completion = json.dumps(order, ensure_ascii=False)
            input_tokens = fake_token_count(load_prompt() + text)
            output_tokens = fake_token_count(completion)
            record = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "trace_id": trace_id,
                "span_id": uuid.uuid4().hex[:16],
                "operation": "chat",  # gen_ai.operation.name
                "provider": "fake-fixtures",  # gen_ai.provider.name（gen_ai.system 已棄用）
                "request_model": "boba-parser-demo",
                "response_model": "boba-parser-demo",
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_ms": latency_ms,
                "finish_reason": "stop",
                "cost_usd": round(
                    input_tokens / 1000 * PRICE_PER_1K_INPUT
                    + output_tokens / 1000 * PRICE_PER_1K_OUTPUT,
                    6,
                ),
                "status": order["status"],
                "hallucination_score": round(0.02 + 0.01 * i, 2),  # 單元二的分數寫回 log
                "session_id": "classroom-demo",
                "user_id": f"student-{i + 1}",
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"已寫入 {out_path}（{len(INPUTS)} 筆）——打開檔案，逐欄對照 README 的欄位表")


if __name__ == "__main__":
    main()
