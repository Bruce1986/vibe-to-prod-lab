# 深讀講義｜單元二：LLM／AI 系統品質驗證

> 投影片：`slides/02-llm-quality.md`（課堂版）；本文是課後深讀版。
> 工具現況查證日：2026-07-15（開課前一週建議複測）。

## Golden Dataset 實務

- **樣本三來源**：真實流量代表題、邊界與地雷（衝突輸入、幻覺誘餌、模糊輸入）、
  事故回歸（每次線上出包收一題，永不再犯）。
- **進版控、走 review**：改 golden set ＝ 改規格；誰能改、怎麼審，
  和 code 一視同仁。
- **判分三層**：exact／規則（含 JSON Schema）→ 語意相似 → LLM-as-judge。
  能用便宜層就不用貴層；本 repo 的 lab 全部用第一層，因此零 API key、
  完全 deterministic。

## Prompt Regression

prompt 也是 code：改 prompt → 跑 golden set → 看 diff → 紅了不上。
本 repo 的實作：`labs/lab2-golden-eval/`（promptfoo 主軌）＋
`tests/test_golden.py`（pytest 備援軌），共用同一批 fixtures。

工具現況（2026-07 查證）：

- **promptfoo**：宣告式 YAML、deterministic assertions（equals／regex／
  is-json＋JSON Schema／javascript…）不用 key 就能跑；官方 GitHub Action。
  <https://www.promptfoo.dev/docs/configuration/expected-outputs/deterministic/>
- **DeepEval**：pytest 風格，但 faithfulness／hallucination／G-Eval 等招牌
  指標全是 LLM-as-judge（要 judge key）。<https://deepeval.com/docs/metrics-introduction>
- **OpenAI Evals 平台將於 2026-11-30 關閉**——選 eval 工具也要評估存續風險。
  <https://developers.openai.com/cookbook/examples/evaluation/moving-from-openai-evals-to-promptfoo>

## Hallucination Detection 方法選單

| 方法 | 原理 | 課堂／CI 可行性 |
|---|---|---|
| LLM-as-judge | 另一個 LLM 逐條裁決 groundedness | 要 key 或本地模型；judge 回應要 cache |
| NLI 小模型 | 幾百 MB 模型判斷「是否被來源支持」 | CPU 可跑、可離線——課堂主力 |
| Citation 查核 | 引文真的在來源裡？來源真的支持該句？ | 純字串比對幾乎免費 |
| Self-consistency | 同題取樣 k 次找矛盾（SelfCheckGPT） | 生成成本 ×k；可用預錄樣本教 |

推薦工具（2026-07 現況）：

- **LettuceDetect**（MIT；17M–210M；token 級標紅；有中文模型）
  <https://github.com/KRLabsOrg/LettuceDetect>
- **HHEM-2.1-Open**（Vectara；110M；Apache-2.0；CPU 約 1.5s／2k tokens）
  <https://huggingface.co/vectara/hallucination_evaluation_model>
- SelfCheckGPT 論文：<https://arxiv.org/abs/2303.08896>
- 商用模型 citation 幻覺率 11%–57% 的量測：<https://arxiv.org/pdf/2604.03173>

## LLM-as-judge 的使用紀律

1. judge 也是 LLM、也會錯——判準要抽樣人工複核。
2. 成本隨 golden set 線性成長——先用規則層濾掉能濾的。
3. CI 裡的 judge 回應要 cache 或預錄，否則紅綠會抖動。

## 免 key 打真模型：GitHub Models

repo 內建加分關（`/live-eval`）：GitHub Actions 的 `GITHUB_TOKEN` 加上
`models: read` 權限即可呼叫 GitHub Models，零註冊零信用卡。
免費層 rate limit 低，只適合小樣本示範。
<https://docs.github.com/en/github-models/quickstart>
