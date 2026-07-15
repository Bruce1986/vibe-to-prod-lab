# Lab 2｜Golden Dataset 與 Prompt Regression（約 20 分鐘）

目標：讓「prompt 被改壞」這件事**被 CI 抓住**——這就是 LLM 世界的回歸測試。

場景：泡泡堂的點餐 prompt 已上線（`app/prompts/order_prompt.txt`），
golden dataset 有 6 筆金標準（本資料夾 `tests.yaml`，預錄回應在
`fixtures/llm_responses.json`）。

## 0. 先看綠色基準線（2 分鐘）

到你 repo 的 GitHub Actions 看 `quality` workflow 的 `golden-eval` job（綠）。
本機有 Node 的人可以選配跑：

```bash
npx promptfoo@0.121.19 eval -c labs/lab2-golden-eval/promptfooconfig.yaml
```

（第一次會下載套件；教室網路慢就直接用 CI 看結果。）

## 1. 情境劇：同事讓 AI「精簡」了 prompt（5 分鐘）

Vibe coding 的常見事故：AI 幫忙「優化」prompt，順手把看似囉嗦的約束刪掉了。
動手重演——打開 `app/prompts/order_prompt.txt`，**刪掉
「配料只能使用菜單配料：…」那一整行**，commit 並 push。

## 2. 看安全網收網（5 分鐘）

GitHub Actions → `quality` → `golden-eval` 轉紅。打開 log 讀 promptfoo 的表格：

- 哪 5 筆掛了？各是哪種錯（型別錯、枚舉外、幻覺配料、不該瞎猜）？
- 哪一筆**沒**掛？穩定 case 為什麼也有存在價值？
- 同時注意 `deploy-gate` job：紅燈時它跑了嗎？（這就是 gate）

## 3. 修復並回綠（3 分鐘）

把那一行加回去（`git revert` 或手動改回）→ push → 回綠。

> 機制透明化：本 lab 的 mock provider 以「配料只能使用菜單」這個關鍵句判斷
> prompt 品質（`mock_provider.js`，教學模擬器）。真實世界的等效改寫當然有效，
> 但在這個模擬器裡請保留關鍵句；想對**真**模型驗證，就去打加分關 `/live-eval`。

## 4. 加一筆你自己的 golden case（5 分鐘）

1. `fixtures/llm_responses.json` 加一筆輸入（`good`／`sloppy` 兩變體）
2. `tests.yaml` 加一個 test 區塊（`vars.input` 要與 fixtures 的 key 一字不差）
3. （建議）`tests/golden_cases.json` 也加同一筆，pytest 備援軌保持同步

push 後 `golden-eval` 仍綠即驗收。

## 加分關：`/live-eval`

用 GitHub Models **免 API key** 打真 LLM，看真模型過不過同一套契約。
在 Claude Code 或 VS Code Copilot Chat 輸入 `/live-eval`，照指示操作。
紅色不是壞事——那是「不可預測性被量測到」的證據。
