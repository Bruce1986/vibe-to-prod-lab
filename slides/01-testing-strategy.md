---
marp: true
theme: default
paginate: true
headingDivider: 2
footer: '從 Vibe Coding 到 Production Architecture ｜ 下午場・Bruce'
style: |
  section { font-size: 26px; }
  section code { font-size: 0.85em; }
  section table { font-size: 0.78em; }
  section pre { font-size: 0.72em; }
---

# 單元一｜AI 時代的測試策略

**從 Vibe Coding 到 Production Architecture** — 下午場
講師：Bruce ｜ 2026-08-18（二）｜ 臺大計中 206

教材 repo：`github.com/Bruce1986/vibe-to-prod-lab`

<!-- 13:30 開講，本段 25 分。開場前確認大家已完成 Use this template + clone（開場 10 分鐘做過）。這一頁停留 30 秒：報 repo 名，請還沒 clone 的人現在按 Use this template。 -->

## 下午場地圖

1. **測試策略**：Unit / Integration / Contract / Regression ← 現在
2. **LLM 品質驗證**：Golden Dataset、Prompt Regression、幻覺檢測
3. **Production 品質工作流**：CI/CD、Observability、AI 品質監控

貫穿範例：**珍奶點餐 bot**（口語訂單 → 結構化 JSON）
每段講授後都有 15–20 分鐘動手 lab；AI 助理輸入 `/course-help` 隨時找路

全程**零 API key**——LLM 用預錄回放，而 determinism 本身就是教材

<!-- 2 分。強調三段是一條線：先會測程式（單元一）→ 再會測 AI（單元二）→ 最後全部自動化上線（單元三）。順帶預告與上午的關係：Jeff 管「生成前」（架構、spec），我們管「生成後」（驗證、部署）。 -->

## AI 時代，為什麼測試反而更重要

- 生成速度 ↑↑，但**作者對程式碼沒有「親手寫過的記憶」**
  - 你 review 自己手寫的 code：讀第二次
  - 你 review AI 生成的 code：**其實是讀第一次**
- AI 改 code 又快又大膽——沒有安全網＝高速公路上蒙眼換輪胎
- 信任來源轉移：「我寫的我知道」→「**驗證過的才算數**」

<!-- 2 分。這頁是整個下午的世界觀。金句放最後一行。可以問現場：「有多少人 merge 過自己沒逐行讀完的 AI diff？」——舉手的人就是目標聽眾。 -->

## 不寫測試才會沒時間：成本算給你看

| | 有 Unit Test | 沒有 Unit Test |
|---|---|---|
| 發現錯誤 | 0.5 秒（測試跑出來） | Build 2h＋QA 1h 之後 |
| 理解問題 | 立刻（就在剛改的地方） | 重現＋理解 1h |
| 修正＋驗證 | 15 分鐘 | 15 分鐘＋再一輪 Build/QA |
| **一個 bug 的週期** | **≈ 0.25 小時** | **≈ 7.25 小時** |

差距 **29 倍**；保守估算也有 2.5 倍。200 個 bug ＝ 1,400 小時。
AI 時代 bug 的「生成速率」也變快了——乘數效應更大。

<!-- 2 分。出處是我 2023 的文章（深讀講義有連結）。重點在最後一行：AI 讓分子（bug 數）變大，所以每個 bug 的除錯成本更要壓下來。 -->

## 測試金字塔（AI 專案版）

```
        ▲   E2E／人工驗收        最慢、最貴、最少
       ▲▲   Golden-set eval      prompt 的回歸網（單元二）
      ▲▲▲   Contract             LLM 輸出契約
     ▲▲▲▲   Integration          層與層的接縫
    ▲▲▲▲▲   Unit                 最快、最多、可窮舉邊界
```

- 原則不變：**下層越厚越好**——快的測試多跑，慢的測試守關鍵
- AI 專案多了兩層新東西：**契約**與 **golden**，今天下午的主角

<!-- 2 分。強調這不是推翻金字塔、是加蓋兩層。很多人以為 LLM 專案「沒辦法測」，其實是金字塔上層長出了新形狀。 -->

## AI 生成程式碼的三個特有風險

| 風險 | 長相 | 哪層防線接住 |
|---|---|---|
| **幻覺 API** | 呼叫不存在的函式／參數／套件 | 型別檢查＋lint＋單元測試 |
| **邊界漏光** | 空值、逾時、部分失敗沒處理 | 單元測試窮舉邊界 |
| **看起來很對** | 流暢自信、細節錯誤 | 契約＋回歸＋review |

共同解法：**AI 生成的 code 用更嚴的標準驗**——
因為沒有任何人真的「寫過」它。

<!-- 2.5 分。第三個風險最陰險：AI 的錯誤不是亂碼、是「合理但錯」。這頁為 Code Review 原則（結尾發的 checklist）埋伏筆。 -->

## 單元測試：快、準、可窮舉

可測試性是**設計出來的**：依賴注入、面向介面（呼應上午的 Dependency Rule）

```python
# tests/test_service.py — 不碰網路、不碰 LLM、毫秒級
def test_quantity_over_limit_rejected(self):
    with pytest.raises(OrderRuleError, match="10"):
        validate_business_rules(make_order(quantity=11))

def test_pure_tea_with_pudding_rejected(self):
    with pytest.raises(OrderRuleError, match="布丁"):
        validate_business_rules(make_order(name="冬瓜茶", toppings=["布丁"]))
```

`make_order(**overrides)`：每個測試只寫它在乎的欄位——測試也要可維護

<!-- 2.5 分。現場開 tests/test_service.py 對照。強調兩件事：(1) 測的是純函式，所以能窮舉；(2) helper 讓測試意圖一眼可讀。 -->

## 整合測試：接縫處才會漏水

LLM 是外部依賴 → 藏在 `LLMClient` 介面後，測試注入 **FakeLLMClient**

```python
class LLMClient(Protocol):
    def complete(self, prompt: str, user_input: str) -> str: ...

# 測試裡：快、免費、deterministic——還能強制回放「壞輸出」
client = FakeLLMClient(variant="sloppy")
with pytest.raises(OrderContractError):
    parse_order("一杯大杯珍珠奶茶全糖去冰，加跳跳糖", client)
```

介面隔離的紅利：單元測試不花錢、錯誤路徑**想測就測**
（呼應上午 Hexagonal 的 LLM Provider 抽象——契約就打在這個 port 上）

<!-- 2.5 分。這頁是與上午最強的銜接點：Jeff 講 Ports & Adapters，我們示範「有了 port，測試才有地方插 fake」。 -->

## 契約測試：LLM 輸出是不可信的外部輸入

`app/schemas/order.schema.json` ＝ 給 LLM 輸出簽的合約（spec 的可執行形式）

```json
"sweetness": { "enum": [0, 30, 50, 70, 100] },
"ice":       { "enum": ["正常冰", "少冰", "微冰", "去冰", "熱"] },
"toppings":  { "items": { "enum": ["珍珠", "波霸", "椰果", "仙草", "布丁"] } },
"quantity":  { "type": "integer", "minimum": 1 }
```

- 幻覺配料「跳跳糖」？**枚舉擋掉**。甜度「半糖」字串？**型別擋掉**
- schema 管不到的跨欄位邏輯（純茶不加布丁）→ 業務規則層
- **分層把關，錯誤訊息各自說人話**

<!-- 2.5 分。投影 schema 片段時指著 enum 講：「這一行就是幻覺的絕緣體」。分層：JSON 解析 → schema → 業務規則，三層錯誤型別不同（OrderParseError / OrderContractError / OrderRuleError）。 -->

## 契約要雙向驗證，缺一不可

```python
# tests/test_contract.py
@pytest.mark.parametrize("user_input", CASE_KEYS)
def test_good_variants_satisfy_contract(user_input):      # 方向一
    jsonschema.validate(FIXTURES[user_input]["good"], load_schema())

@pytest.mark.parametrize("user_input", SCHEMA_INVALID_SLOPPY)
def test_known_sloppy_variants_violate_contract(user_input):  # 方向二
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(FIXTURES[user_input]["sloppy"], load_schema())
```

- 方向一：正常輸出全過——契約**不誤殺**
- 方向二：已知壞輸出必擋——契約**抓得住**
- 只驗單向的契約是裝飾品

<!-- 2 分。很多團隊只寫方向一。方向二（known-bad 樣本必須被擋）才是契約的牙齒——這也是 fixtures 裡 sloppy 變體存在的理由：它們是「刻意保存的壞範例」。 -->

## 回歸測試：AI 改 code 的安全網

- 回歸 ＝「昨天好的，今天還好嗎」
- AI 重構、AI 修 bug、AI「順手優化」——每一次都該有網子接著
- 沒有回歸網的 vibe coding ＝ 不斷疊加**未驗證的信任**
- Lab 1 會親手體驗：改壞一行 → 紅 → 改回 → 綠
- 單元二把同一個概念延伸到 prompt：**prompt 也是 code**

<!-- 1.5 分。過場頁，把回歸的概念說清楚就好，細節留給 lab 和單元二。 -->

## 本 repo 對照表（lab 的地圖）

| 測試層 | 檔案 | 接住什麼 |
|---|---|---|
| Unit | `tests/test_service.py`（Rules 類） | 業務邏輯邊界 |
| Integration | `tests/test_service.py`（Integration 類） | 全流程接縫 |
| Contract | `tests/test_contract.py`＋`order.schema.json` | 幻覺／型別／枚舉 |
| Regression | `tests/test_golden.py`（單元二細講） | prompt 改壞 |

`python -m pytest -q` 一次全跑，**0.2 秒**——這就是下層厚的紅利

<!-- 1.5 分。報一個真數字：26 個測試 0.2 秒。「快到沒有藉口不跑」。 -->

## Lab 1（15 分鐘）

打開 `labs/lab1-testing/README.md`，或對 AI 助理輸入 **`/lab1`**

1. 建環境、`python -m pytest -q`（全綠起點）
2. 完成 `tests/test_lab1_student.py` 兩個 TODO（通過數 +2）
3. 契約手感：親手觸發 `OrderContractError`
4. 回歸手感：改壞一行 → 紅 → 改回 → 綠

卡關就問 AI——但先自己想 **Arrange → Act → Assert**
（AI 助理被設定成先給提示不給答案，這是故意的）

<!-- 13:55–14:10 實作＋提問，14:10–14:18 休息。行間巡場重點：venv 啟動失敗的人（Windows PowerShell 執行原則）、pytest 找不到 app 的人（沒在 repo 根目錄跑）。 -->
