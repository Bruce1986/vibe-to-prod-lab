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

# 單元三｜Production 品質工作流

**CI/CD ・ Automated Testing ・ Observability ・ Logging ・ AI 品質監控**

從 Vibe Coding 到 Production Architecture — 下午場｜Bruce

<!-- 15:16 開講，本段 22 分、12 頁。把前兩單元的驗證「自動化、常態化、可視化」。 -->

## 從「會動」到「能上線」

Production-ready 的三個形容詞：

- **可測試**——單元一、二已就位
- **可觀測**——壞掉時：你會知道、知道在哪、知道多嚴重
- **可維護**——下一個人（或下一個 AI）能安全地改它

AI 專案的殘酷事實：**demo 到 production 的距離，大部分在這三個詞裡**

<!-- 1.5 分。呼應課程副標。「demo 很驚豔、上線變事故」的落差就是本單元要補的。 -->

## CI/CD 解剖：看本 repo 的 quality.yml

```yaml
jobs:
  lint-test:        # 第一關：程式壞掉？（ruff + pytest）
    ...
  golden-eval:      # 第二關：prompt 壞掉？（promptfoo）
    needs: lint-test
    ...
  deploy-gate:      # 第三關：紅了就不部署
    needs: [lint-test, golden-eval]
    ...
```

- 每一關**擋一種壞**；`needs` 串出依賴——這就是 **gate**
- Lab 2 你們弄紅的那次 run：`deploy-gate` 根本沒跑——**它工作了**

<!-- 2.5 分。現場開 Actions 挑一個學員的紅 run，指給大家看 deploy-gate 灰掉的樣子：「保護不是靠人記得，是靠依賴圖」。 -->

## Gate 的哲學

- 部署的資格是**掙來的**，不是預設的
- 人會忘、會累、會「這次先上再說」——**gate 不會**
- 上午的 spec 定義「什麼是對」；下午的 gate 保證「不對就不上」
- 延伸：正式團隊常再加 **manual approval**（人肉 gate）於高風險環境

一句話：**讓「壞的上不去」變成系統性質，不是紀律問題**

<!-- 1.5 分。金句收尾。可帶一句：這也是為什麼 deploy-gate 在示範裡只是 echo——重點是位置，不是內容。 -->

## 你正在看的投影片，就是 CI 的產物

```
slides/*.md（Marp Markdown）
   └─ push ─▶ GitHub Actions：marp-cli 建置 HTML
                 └─▶ GitHub Pages 自動部署
```

- 這份投影片＝`slides/02-…md` 等純文字檔，**進版控、可 diff、可 review**
- 我改一行字 push，兩分鐘後全班看到的網址就是新版
- **管線本身就是教材**——`.github/workflows/slides.yml` 回家慢慢讀

<!-- 1.5 分。自舉梗：現場示範不必真跑，講「上一次 push 就是這樣上來的」即可。 -->

## Observability：三支柱＋LLM 的第四樣

| 支柱 | 回答的問題 | LLM 世界多問一句 |
|---|---|---|
| **Logs** | 發生了什麼 | prompt／輸出內容記不記？（隱私） |
| **Traces** | 一個請求經過哪些步驟 | agent 多步呼叫鏈長什麼樣 |
| **Metrics** | 快不快、掛沒掛 | token 花多少、**品質分數多少** |

第四樣：**eval score**——把單元二的檢測分數當一級公民記下來
（幻覺分數、契約通過率、golden 通過率）

<!-- 2 分。三支柱是舊識，第四樣是新客：品質分數要和延遲、錯誤率平起平坐。 -->

## LLM 呼叫的結構化 log（本 repo 實檔輸出）

```json
{"trace_id": "9f3…", "span_id": "1c7…", "operation": "chat",
 "provider": "fake-fixtures", "request_model": "boba-parser-demo",
 "input_tokens": 412, "output_tokens": 63, "latency_ms": 1.42,
 "finish_reason": "stop", "cost_usd": 0.0001,
 "status": "ok", "hallucination_score": 0.02,
 "session_id": "classroom-demo", "user_id": "student-1"}
```

- 欄位對齊 **OpenTelemetry `gen_ai.*`** 慣例（業界收斂中的標準）
- `trace_id`：把 agent 的多步呼叫串成一條鏈——除錯的救命索
- Lab 3 親手產一份，逐欄對照 README 的欄位表

<!-- 2 分。指三個欄位講：trace_id（串鏈）、hallucination_score（單元二寫回來）、cost_usd（下一頁的哏）。 -->

## OTel gen_ai.* 的三個「現況注意」（2026-07 查證）

1. 全部屬性仍是 **Development**（實驗）狀態——可押注採用，但非 Stable
2. `gen_ai.system` **已棄用** → 改用 `gen_ai.provider.name`（教材照新的）
3. **沒有 cost 欄位**——成本是各平台自己用 tokens × 單價算的

啟示：

- **站在標準上，但知道標準的邊界在哪**
- prompt／completion 內容 OTel 預設**不擷取**——要記就要做 PII 治理

<!-- 1.5 分。第 3 點接上一頁的 cost_usd：那是我們自己算的。PII 一句帶過，深讀講義有展開。 -->

## Demo：Arize Phoenix（跟著看）

```bash
pip install arize-phoenix
phoenix serve        # → http://localhost:6006
```

- **零註冊、零 Docker**、本地跑——教室斷網也能 demo
- OpenInference 自動 instrument：openai／anthropic SDK 兩三行接上
- 看什麼：trace 瀑布圖（每步的輸入輸出／延遲／token）、
  把幻覺分數當 **evaluation 附回 trace**

**品質驗證（單元二）× 可觀測性（單元三）＝ AI 品質監控**

<!-- 3 分（含 demo 切換）。demo 動線：跑預錄 trace 重播 → 點開一條 trace → 指 evaluation 分數。最後一行是兩單元的合流宣言。 -->

## 品質監控＝設計反應，不是收集數據

告警要回答三件事：

- **訊號**：幻覺分數 7 日均線上升？契約失敗率 > 1%？
- **門檻**：多壞才叫壞？——先觀察基線兩週再定，別拍腦袋
- **反應**：誰收到？第一步做什麼？（**runbook**，哪怕只有三行）

閉環回單元二：**每次線上事故 → 收進 golden set → 永不再犯**
（事故不是恥辱，是免費的測資）

<!-- 2 分。closed loop 是本課系統觀的收束點：監控發現 → golden 固化 → CI 防再犯。 -->

## 帶回團隊的三件禮物（templates/）

1. **`AGENTS.sample.md`**——把今天的規範寫給你團隊的 AI 看
   （規範不落地成檔案，AI 就每次都用預設值；複製到 repo root 改名即生效）
2. **`pr-checklist.md`**——AI 時代的 PR 品質清單（作者版＋reviewer 版）
3. **`workflows/quality.sample.yml`**——三關品質管線，換佔位符就能用

外加：這整個 repo 是 **Template**——「Use this template」複製走，
改成你們家的題材，golden set 換成你們家的事故

<!-- 1.5 分。具體交代「回去第一步」：三個檔案各 30 秒導覽。 -->

## Lab 3（15 分鐘）＋ 收尾

打開 `labs/lab3-production/README.md`，或輸入 **`/lab3`**

1. 解剖 `quality.yml` 三關（gate 的意義；回看你 Lab 2 的紅 run）
2. 看 Step Summary——CI 也要說人話
3. `python labs/lab3-production/log_demo.py` → 讀你的 `llm_calls.jsonl`
4. 跟著看 Phoenix demo

之後：15:55 彈性緩衝與自由問答，16:05 總結

**讓 AI 進 production 的，不是信任，是驗證。**

<!-- 15:38–15:55 實作＋提問。16:05–16:10 結尾：回顧三單元一條線（測程式→測 AI→自動化上線）、發三件禮物、最後金句就用這頁最後一行。 -->
