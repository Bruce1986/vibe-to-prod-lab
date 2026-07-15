# Lab 3｜Production 品質工作流（約 15 分鐘）

目標：讀懂一條品質管線，並親手產生一份「LLM 呼叫的結構化 log」。

## 1. 解剖 `.github/workflows/quality.yml`（5 分鐘）

`lint-test → golden-eval → deploy-gate` 三關：

- 哪一關擋「**程式**壞掉」？哪一關擋「**prompt** 壞掉」？
- `deploy-gate` 為什麼要 `needs` 前兩關？（gate 的意義：紅了就不部署）
- 對照你在 Lab 2 弄紅的那次 run：當時 `deploy-gate` 有跑嗎？

## 2. 看 Step Summary（3 分鐘）

Actions 任一次 run → Summary 分頁。CI 不只要紅綠，還要「說人話」的報告——
這跟錯誤訊息要說人話是同一件事。

## 3. 產生你的 LLM 呼叫 log（5 分鐘）

```bash
python labs/lab3-production/log_demo.py
```

打開 repo 根目錄的 `llm_calls.jsonl`（Windows 記事本或 `type llm_calls.jsonl`），
逐欄對照下方欄位表，回答兩個問題：

- `trace_id` 是拿來做什麼的？（提示：多步驟的 agent 呼叫鏈）
- `cost_usd` 為什麼要自己算？（提示：OTel `gen_ai.*` 目前沒有 cost 欄位）

## 4. 講師 demo：Arize Phoenix（跟著看就好）

```bash
pip install arize-phoenix
phoenix serve   # → http://localhost:6006（零註冊、零 Docker）
```

把同一批呼叫變成可視化 trace；再把單元二的幻覺分數當 score 寫回 trace——
**品質驗證（單元二）與可觀測性（單元三）在這裡合流成「AI 品質監控」。**

## LLM 呼叫 log 欄位表（對齊 OpenTelemetry `gen_ai.*` 慣例）

| 欄位 | OTel 對應 | 用途 |
|---|---|---|
| `trace_id` / `span_id` | trace context | 把多步驟呼叫串成一條鏈 |
| `operation` | `gen_ai.operation.name` | chat／embeddings／… |
| `provider` | `gen_ai.provider.name` | 注意：舊欄位 `gen_ai.system` 已棄用 |
| `request_model` / `response_model` | `gen_ai.request.model`／`gen_ai.response.model` | 路由或別名後兩者可能不同，都要記 |
| `input_tokens` / `output_tokens` | `gen_ai.usage.*` | 成本與容量規劃的原料 |
| `latency_ms` | `gen_ai.client.operation.duration` | 體感與 SLO |
| `finish_reason` | `gen_ai.response.finish_reasons` | stop／length／tool_calls |
| `cost_usd` | （OTel 沒有這欄） | 各平台自行以 tokens×單價換算 |
| `hallucination_score` | （無標準欄位；常叫 score） | AI 品質監控與告警的訊號 |
| `session_id` / `user_id` | `gen_ai.conversation.id`／`user.id` | 追個案、看留存 |

> 隱私提醒：prompt／completion 內容在 OTel 慣例中**預設不擷取**——
> 要記錄就要自覺做 PII 治理，這是把 AI 送進 production 的必修題。
