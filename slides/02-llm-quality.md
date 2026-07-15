---
marp: true
theme: default
paginate: true
headingDivider: 2
---

# 單元二｜LLM／AI 系統品質驗證

Golden Dataset ・ Prompt Regression ・ Hallucination Detection ・ Evaluation Pipeline

從 Vibe Coding 到 Production Architecture — 下午場｜Bruce

## LLM 品質問題長什麼樣

- **幻覺**：發明不存在的東西（菜單上沒有的「跳跳糖」、不存在的 API）
- **格式違約**：該回 JSON 卻多話、欄位型別錯、枚舉外的值
- **瞎猜**：資訊不足時不反問，硬編一個答案
- **風格／行為漂移**：改了 prompt 或換了模型版本，輸出悄悄變了

共同點：**傳統測試的「輸入 X 必得 Y」框不住它們**

## 為什麼傳統測試不夠

- 非確定性：同樣輸入，兩次輸出可能不同
- 對錯是**程度**不是布林：0.87 分的答案算過嗎？
- 改 prompt 的影響是**全域的**：改一句話，六個場景三個變壞
- 所以需要：**成批的金標準＋自動判分＋進 CI**——這就是 eval

## Golden Dataset：你的 AI 考古題庫

- 一筆 golden case ＝ 輸入 ＋「金標準」該滿足的斷言
- 樣本從哪來：
  - **真實流量**的代表題（最常見的訂單長相）
  - **邊界與地雷**（衝突輸入、幻覺誘餌、模糊輸入）
  - **事故回歸**：每次線上出包，就把該案例收進題庫（永不再犯）
- 跟 code 一樣**進版控、走 review**——改 golden set 就是改規格

## 判分三層：從便宜到昂貴

| 層 | 方法 | 成本 | 例 |
|---|---|---|---|
| 1 | exact／規則（含 JSON Schema） | 免費、快、穩 | `sweetness === 50`、過契約 |
| 2 | 語意相似（embedding、ROUGE…） | 便宜 | 摘要類任務 |
| 3 | LLM-as-judge | 貴、judge 也會錯 | 「回答是否有禮貌且未瞎猜」 |

**原則：能用第 1 層就不要用第 3 層**——本課 lab 全部用第 1 層，
所以能零 API key、完全 deterministic。

## Prompt Regression：prompt 也是 code

- 改 prompt ＝ 改行為 ＝ 需要回歸測試
- 流程：改 prompt → 跑 golden set → 看 diff 報告 → 紅了就別上
- Lab 2 情境劇：AI 幫同事「精簡」prompt、刪了約束行
  → golden set 六筆掛五筆 → **CI 把事故擋在 merge 之前**
- 這就是「AI 生成內容不可預測」的解法：**不可預測沒關係，量測它**

## Evaluation Pipeline：把 eval 接進 CI

```
push ──▶ lint-test（程式壞掉？）
              └─▶ golden-eval（prompt 壞掉？）
                       └─▶ deploy-gate（都綠才准部署）
```

- 本 repo 用 promptfoo：golden case 寫在 YAML、斷言宣告式
- mock provider 回放預錄 fixtures → 教室裡零 key、零網路依賴
- 加分關 `/live-eval`：GitHub Models **免 key 打真模型**，
  看真 LLM 過不過同一套契約

## Hallucination Detection：方法選單

| 方法 | 原理 | 成本／離線 |
|---|---|---|
| LLM-as-judge | 用另一個 LLM 逐條裁決「有沒有依據」 | 貴；需 API 或本地模型 |
| **NLI 小模型** | 幾百 MB 分類模型判斷「是否被來源支持」 | **免費、CPU、可離線** |
| Citation 查核 | 驗證引文真的存在於來源且支持該句 | 幾乎免費 |
| Self-consistency | 同題取樣 k 次，幻覺會彼此矛盾 | 生成成本 ×k |

## Demo：把幻覺標出來（講師機）

- **LettuceDetect**（MIT、17M–210M 參數、CPU 即時）：
  token 級把幻覺片段「螢光筆標紅」——有中文模型
- **HHEM-2.1-Open**（Vectara、110M、Apache-2.0）：
  給 (context, answer) 打 0–1 分，與 span 標記互相印證
- 商用模型的 citation 幻覺率實測 **11%–57%**（2026 研究）——
  「有附來源」不等於「來源真的這樣說」

## LLM-as-judge 的三個誠實提醒

1. **Judge 也會錯**：它自己就是個 LLM——judge 的判準要抽樣人工複核
2. **成本**：每筆檢查都是一次推論——golden set 大了要算錢
3. **可重現性**：judge 回應要 cache／預錄，否則 CI 紅綠會抖動

工具現況（2026-07）：promptfoo（宣告式、CI 友善）、DeepEval（pytest 風格、
指標幾乎都要 judge key）；**OpenAI Evals 平台 2026-11-30 關閉**——
工具選型要看存續風險，這也是本課的一課。

## Lab 2（20 分鐘）

打開 `labs/lab2-golden-eval/README.md`，或輸入 **`/lab2`**

1. 看綠色基準線（Actions → golden-eval）
2. 情境劇：刪掉 prompt 的約束行 → push → 看安全網收網（讀紅色報告）
3. 修復回綠
4. 加一筆你自己的 golden case
5. 加分關：**`/live-eval`** 免 key 打真模型

紅色不是壞事——是不可預測性被量測到
