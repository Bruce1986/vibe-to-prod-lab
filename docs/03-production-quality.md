# 深讀講義｜單元三：Production 品質工作流

> 投影片：`slides/03-production-quality.md`（課堂版）；本文是課後深讀版。
> 工具現況查證日：2026-07-15（開課前一週建議複測）。

## 品質管線的設計語言

本 repo 的 `.github/workflows/quality.yml` 是最小可教範例：

- `lint-test`：擋「程式壞掉」（ruff＋pytest）
- `golden-eval`：擋「prompt 壞掉」（promptfoo，mock 回放零 key）
- `deploy-gate`：`needs` 前兩關——紅了就不部署，這就是 gate

`slides.yml` 則示範「建置＋部署」：Marp Markdown → HTML → GitHub Pages，
投影片本身就是 CI 產物。

## LLM Observability

三支柱（logs／traces／metrics）之上，LLM 系統多一個一級公民：**eval score**。
把單元二的幻覺分數、契約通過率當 metrics 記錄與告警，就是「AI 品質監控」。

### 最小 log schema（對齊 OTel `gen_ai.*`）

欄位表見 `labs/lab3-production/README.md`；三個 2026-07 現況注意：

1. `gen_ai.*` 屬性目前**全部仍是 Development 狀態**（沒有 Stable）——
   可押注採用，教材要註明非定案。
   <https://opentelemetry.io/docs/specs/semconv/registry/attributes/gen-ai/>
2. `gen_ai.system` 已棄用，改用 `gen_ai.provider.name`。
3. **OTel 沒有 cost 欄位**——成本由平台以 tokens×單價自行換算。

另：prompt／completion 內容預設**不**擷取（`gen_ai.input.messages`／
`gen_ai.output.messages` 需顯式開啟）——記內容就要做 PII 治理。

## 工具選型（2026-07 查證）

| 工具 | 定位 | 教室可行性 |
|---|---|---|
| **Arize Phoenix** | 本地 trace UI（`pip install arize-phoenix` → `phoenix serve`） | **零註冊、零 Docker**——課堂首選 |
| Langfuse Cloud | 商用級 dashboard，免費層 50k units／月 | 需註冊；self-host 要 Docker 六件套，教室不可行 |
| LangSmith | LangChain 生態最深 | 免費層 5k traces；要 key |
| OpenLLMetry | OTel 式 instrument 層，接任何後端 | 進階選讀 |

- Phoenix：<https://pypi.org/project/arize-phoenix/>（Elastic License 2.0；
  OpenInference 對 openai／anthropic SDK 自動 instrument）
- Langfuse 定價：<https://langfuse.com/pricing>
- OpenLLMetry：<https://github.com/traceloop/openllmetry>

## 監控是設計反應，不是收集數據

告警三問：訊號（幻覺分數 7 日均線？契約失敗率？）、門檻（先量基線再定）、
反應（誰收到、第一步做什麼——runbook）。
閉環回單元二：每次線上事故 → 收進 golden set → 永不再犯。

## 延伸案例

- 生產環境可靠性的真實案例（Discord 基礎設施）：
  <https://brucejhang.com/tw/topics/knowledge/discord-infrastructure-app.html>
- SRE 與無咎檢討文化：
  <https://brucejhang.com/tw/topics/knowledge/google-software-engineering-deep-dive-article.html>
