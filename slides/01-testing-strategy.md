---
marp: true
theme: default
paginate: true
headingDivider: 2
---

# 單元一｜AI 時代的測試策略

從 Vibe Coding 到 Production Architecture — 下午場
講師：Bruce ｜ 2026-08-18 ｜ 臺大計中

教材 repo：`github.com/Bruce1986/vibe-to-prod-lab`

## 下午場地圖

1. **測試策略**：Unit / Integration / Contract / Regression ← 現在
2. **LLM 品質驗證**：Golden Dataset、Prompt Regression、幻覺檢測
3. **Production 品質工作流**：CI/CD、Observability、AI 品質監控

貫穿範例：**珍奶點餐 bot**（口語訂單 → 結構化 JSON）
三個 lab、全程零 API key（預錄回放——determinism 本身就是教材）

## AI 時代，為什麼測試反而更重要

- 生成速度 ↑↑，但**作者對程式碼沒有「親手寫過的記憶」**
- 上午的架構與 spec 管「生成前」；測試管「生成後」
- AI 改 code 又快又大膽——沒有安全網，就是在高速公路上蒙眼換輪胎
- 品質的信任來源從「我寫的我知道」變成「**驗證過的才算數**」

## 不寫測試才會沒時間：成本算給你看

| | 有 Unit Test | 沒有 Unit Test |
|---|---|---|
| 發現錯誤 | 0.5 秒（測試跑出來） | Build 2h + QA 1h 後 |
| 理解問題 | 立刻（就在剛改的地方） | 重現＋理解 1h |
| 修正＋驗證 | 15 分鐘 | 15 分鐘＋再一輪 Build/QA |
| **一個 bug 的週期** | **約 0.25 小時** | **約 7.25 小時** |

差距 **29 倍**。200 個 bug ＝ 1,400 小時。
（保守估算也有 2.5 倍——詳見講義連結）

## 測試金字塔（AI 專案版）

```
        ▲  E2E／人工驗收（最慢、最貴、最少）
       ▲▲  Golden set eval（prompt 的回歸網）← 單元二
      ▲▲▲  Contract（LLM 輸出契約）
     ▲▲▲▲  Integration（接縫處）
    ▲▲▲▲▲  Unit（最快、最多、可窮舉邊界）
```

原則不變：**下層越厚越好**；AI 專案多了兩層新東西——契約與 golden。

## 單元測試：快、準、可窮舉

- 測「純邏輯」：不碰網路、不碰 LLM、毫秒級
- 可測試性是**設計出來的**：DI、面向介面（呼應上午 Clean Architecture）
- 本 repo：`validate_business_rules()` 直接餵 dict 測
  - 數量上限、純茶不加布丁——邊界一條一條列

```python
with pytest.raises(OrderRuleError, match="10"):
    validate_business_rules(make_order(quantity=11))
```

## 整合測試：接縫處才會漏水

- 單元全綠 ≠ 組起來能動——測「層與層的接縫」
- LLM 是外部依賴 → 藏在 `LLMClient` 介面後，測試注入 **FakeLLMClient**
  - 快、免費、deterministic；還能強制回放「壞輸出」測錯誤路徑

```python
client = FakeLLMClient(variant="sloppy")   # 強制回放壞輸出
with pytest.raises(OrderContractError):
    parse_order("…加跳跳糖", client)
```

## 契約測試：LLM 輸出是「不可信的外部輸入」

- JSON Schema ＝ 給 LLM 輸出簽的合約：型別、枚舉、必填
- 雙向驗證，缺一不可：
  - 所有正常輸出**必須通過**（契約不誤殺）
  - 已知壞輸出**必須被擋**（契約抓得住：幻覺配料、型別錯、枚舉外）
- 接上午的 Spec：schema 就是 spec 的可執行形式
- schema 管不到的跨欄位邏輯 → 業務規則層（分層把關）

## 回歸測試：AI 改 code 的安全網

- 回歸 ＝「昨天好的，今天還好嗎」
- AI 重構、AI 修 bug、AI「順手優化」——每一次都該有網子接著
- 沒有回歸網的 vibe coding ＝ 不斷疊加「未驗證的信任」
- 單元二把這個概念延伸到 prompt：**prompt 也是 code**

## 本 repo 對照表

| 測試層 | 檔案 | 接住什麼 |
|---|---|---|
| Unit | `tests/test_service.py`（Rules 類） | 業務邏輯邊界 |
| Integration | `tests/test_service.py`（Integration 類） | 全流程接縫 |
| Contract | `tests/test_contract.py` ＋ `order.schema.json` | 幻覺／型別／枚舉 |
| Regression | `tests/test_golden.py`（單元二細講） | prompt 改壞 |

## Lab 1（15 分鐘）

打開 `labs/lab1-testing/README.md`，或直接在 AI 助理輸入 **`/lab1`**

1. 建環境、跑 `python -m pytest -q`（全綠起點）
2. 完成 `tests/test_lab1_student.py` 兩個 TODO（通過數 +2）
3. 契約手感：親手觸發 `OrderContractError`
4. 回歸手感：改壞一行 → 紅 → 改回 → 綠

卡關就問你的 AI——但先自己想 Arrange → Act → Assert
