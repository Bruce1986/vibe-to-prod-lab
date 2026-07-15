"""LLM 客戶端介面與教學用 Fake 實作。

課堂原則：外部服務（尤其 LLM API）藏在介面後面，才 mock 得掉、測得起、換得掉。
本 repo 的所有測試與 eval 都走 FakeLLMClient 回放預錄 fixtures，零 API key。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

FIXTURES_PATH = Path(__file__).resolve().parent.parent / "fixtures" / "llm_responses.json"

# Fake 判斷 prompt 品質的關鍵約束句——與 labs/lab2-golden-eval/mock_provider.js
# 使用同一條規則；拿掉這句約束，回放就會退化成 sloppy 變體（模擬 prompt 回歸）。
PROMPT_QUALITY_MARKER = "配料只能使用菜單"


class LLMClient(Protocol):
    """所有 LLM 供應商的最小介面：給 prompt 與使用者輸入，回一段文字。"""

    def complete(self, prompt: str, user_input: str) -> str:
        ...


class FakeLLMClient:
    """讀取預錄 fixtures 回放回應的教學用客戶端（deterministic）。

    variant:
      - "auto"（預設）：prompt 含關鍵約束句時回放 good、否則回放 sloppy，
        模擬「prompt 品質影響輸出品質」，讓 golden 測試抓得到 prompt 回歸。
      - "good" / "sloppy"：強制回放指定變體（測試錯誤處理路徑時使用）。
    """

    def __init__(self, fixtures_path: Path = FIXTURES_PATH, variant: str = "auto") -> None:
        if variant not in {"auto", "good", "sloppy"}:
            raise ValueError(f"未知的 variant：{variant}")
        self._fixtures = json.loads(Path(fixtures_path).read_text(encoding="utf-8"))
        self._variant = variant

    def complete(self, prompt: str, user_input: str) -> str:
        entry = self._fixtures.get(user_input, self._fixtures["__default__"])
        if self._variant == "auto":
            variant = "good" if PROMPT_QUALITY_MARKER in prompt else "sloppy"
        else:
            variant = self._variant
        payload = entry.get(variant, entry["good"])
        if isinstance(payload, str):
            return payload  # 刻意壞掉的非 JSON 教學樣本，原樣回傳
        return json.dumps(payload, ensure_ascii=False)
