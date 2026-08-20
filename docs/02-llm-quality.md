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

## 零 token 考真模型：把小模型跑在 CI runner 上

repo 內建加分關（`/local-eval`）：eval-local workflow 在 GitHub Actions 的
runner 上安裝 Ollama、拉 qwen2.5:1.5b，對同一份 golden 題庫裡的 3 題小樣卷
（`tests.small.yaml`；主線 golden 軌 `tests.yaml` 是 6 題）推論——
**零 API key、零外部帳號、零費用**，全程約 3 分鐘。它是 monitor 不是
gate：小模型上當幻覺誘餌、對模糊輸入瞎猜都是預期內的「資訊」。

> 存續風險的活教材：本關最初以 **GitHub Models**（`GITHUB_TOKEN`＋
> `models: read` 的免費推論）實作，2026-07-15 實測 gpt-4o-mini 3/3；
> 該服務 **2026-07-30 全面退役**（7/1 公告），與 OpenAI Evals（11/30 關閉）
> 同一年謝幕。因 golden set 與 provider 解耦，題目與 prompt 一個字都沒改，
> 斷言要驗的東西也一樣；但誠實地說，遷移不只「改一行」——斷言的**寫法**
> 得改成 try/catch＋防禦性存取（小模型會夾帶 ```json 圍欄、會輸出殘缺結構，
> 原本的單行直接存取會拋 Error 而不是判 Fail），provider 換掉後還得補生成參數
> （`num_predict: 512`，否則 Ollama 預設輸出上限會把 JSON 攔腰截斷，這是
> 實際踩到才發現的），以及整套「模型從哪來」的 runtime 佈建（安裝 Ollama、
> 拉模型）。**平台會死，eval 資產不會——但搬家還是要出力。**
> <https://github.blog/changelog/2026-07-01-github-models-is-being-fully-retired-on-july-30-2026/>
