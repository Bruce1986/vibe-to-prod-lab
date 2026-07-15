---
marp: true
theme: default
paginate: true
headingDivider: 2
---

# 單元三｜Production 品質工作流

CI/CD ・ Automated Testing ・ Observability ・ Logging ・ AI 品質監控

從 Vibe Coding 到 Production Architecture — 下午場｜Bruce

## 從「會動」到「能上線」

Production-ready 的三個形容詞（也是課程副標）：

- **可測試**（單元一、二已就位）
- **可觀測**：壞掉時，你會知道、知道在哪、知道多嚴重
- **可維護**：下一個人（或下一個 AI）能安全地改它

今天的最後一塊拼圖：把前兩單元的驗證**自動化、常態化、可視化**

## CI/CD 解剖：就看本 repo 的 quality.yml

```
push ──▶ lint-test ──▶ golden-eval ──▶ deploy-gate
          ruff+pytest    promptfoo        （示範）
          程式壞掉？      prompt 壞掉？     紅了就不部署
```

- 每一關**擋一種壞**；`needs` 串出依賴——這就是 gate
- Lab 2 你們弄紅的那次 run：deploy-gate 根本沒跑——**它工作了**
- 你正在看的這份投影片，就是 `slides.yml` 從 Markdown 建置、
  自動部署到 GitHub Pages 的——**管線本身就是教材**

## Observability：三支柱＋LLM 的第四樣

| 支柱 | 傳統世界 | LLM 世界多問一句 |
|---|---|---|
| Logs | 發生了什麼 | prompt／輸出記不記？（隱私！） |
| Traces | 一個請求經過哪些步驟 | agent 的多步呼叫鏈長什麼樣 |
| Metrics | 快不快、掛沒掛 | token 花多少、**品質分數多少** |

第四樣：**eval score**——把單元二的檢測分數當一級公民記下來

## LLM 呼叫的最小 log schema

```json
{"trace_id":"…","span_id":"…","operation":"chat",
 "provider":"…","request_model":"…","response_model":"…",
 "input_tokens":123,"output_tokens":45,"latency_ms":210,
 "finish_reason":"stop","cost_usd":0.00012,
 "hallucination_score":0.03,"session_id":"…","user_id":"…"}
```

- 欄位對齊 **OpenTelemetry `gen_ai.*`** 慣例（業界正在收斂的標準）
- Lab 3 會親手產一份這個檔

## OTel gen_ai.* 的三個「現況注意」

1. 全部屬性目前仍是 **Development**（實驗）狀態——可押注採用，但非 Stable
2. `gen_ai.system` 已棄用 → 改用 `gen_ai.provider.name`（教材照新的教）
3. **沒有 cost 欄位**——成本是各平台自己用 tokens × 單價算的

啟示：站在標準上，但知道標準的邊界在哪

## Demo：Arize Phoenix（講師機）

```bash
pip install arize-phoenix
phoenix serve        # → http://localhost:6006
```

- **零註冊、零 Docker**、本地跑——教室斷網也能 demo
- OpenInference 自動 instrument：openai／anthropic SDK 兩三行接上
- 把幻覺分數當 evaluation 寫回 trace：
  **品質驗證（單元二）×可觀測性（單元三）＝ AI 品質監控**

## AI 品質監控：從數據到反應

- 記了分數還不夠——**監控是設計反應，不是收集數據**
- 告警要問三件事：
  - 訊號：幻覺分數７日均線上升？契約失敗率 > 1%？
  - 門檻：多壞才叫壞？（先觀察基線再定）
  - 反應：誰收到？第一步做什麼？（runbook）
- 每次線上事故 → 收進 golden set → 永不再犯（回到單元二的閉環）

## 帶回團隊的三件禮物（templates/）

1. `AGENTS.sample.md`——把今天的規範寫給你團隊的 AI 看
   （規範不落地成檔案，AI 就每次都用預設值）
2. `pr-checklist.md`——AI 時代的 PR 品質清單（作者版＋reviewer 版）
3. `workflows/quality.sample.yml`——三關品質管線，換佔位符就能用

## Lab 3（15 分鐘）＋ 收尾

打開 `labs/lab3-production/README.md`，或輸入 **`/lab3`**

1. 解剖 `quality.yml` 三關（gate 的意義）
2. 看 Step Summary（CI 也要說人話）
3. `python labs/lab3-production/log_demo.py` → 讀你的 `llm_calls.jsonl`
4. 跟著看 Phoenix demo

最後 5 分鐘：總結——**讓 AI 進 production 的不是信任，是驗證**
