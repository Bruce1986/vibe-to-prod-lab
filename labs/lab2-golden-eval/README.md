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
> 但在這個模擬器裡請保留關鍵句；想對**真**模型驗證，就去打加分關 `/local-eval`。

## 4. 加一筆你自己的 golden case（5 分鐘）

1. `fixtures/llm_responses.json` 加一筆輸入（`good`／`sloppy` 兩變體）
2. `tests.yaml` 加一個 test 區塊（`vars.input` 要與 fixtures 的 key 一字不差）
3. （建議）`tests/golden_cases.json` 也加同一筆，pytest 備援軌保持同步

push 後 `golden-eval` 仍綠即驗收。

## 加分關：`/local-eval`

讓一個**真的 LLM** 考 golden 題庫裡的 3 題小樣卷——本地小模型
（Ollama qwen2.5:1.5b）直接跑在 GitHub Actions 的 runner 上，
**零 API key、零外部帳號、零費用**。在 Claude Code 或 VS Code Copilot Chat
輸入 `/local-eval`，照指示操作（或自己 `gh workflow run eval-local.yml`）。

- 這是 **monitor** 不是 gate：紅色是資訊，不擋部署。
- **考卷範圍**：加分關讀的是 `tests.small.yaml`（3 題，主線 `tests.yaml`
  6 題的子集），因為 CPU 推論慢、題數要壓。**所以上面第 4 步你自己加的
  那筆 case 不會出現在加分關**——它跑在主線 `golden-eval` 上。想讓小模型
  也考你那題，把它一併加進 `tests.small.yaml`。
- 對照組：雲端 gpt-4o-mini 曾以這 3 題拿 3/3；1.5B 小模型首測 1/3——
  幻覺誘餌上當、模糊輸入瞎猜。同卷不同模型的分數差，就是 eval 的價值。
  （誠實的但書：3/3 那次跑的是舊版單行斷言，1/3 跑的是現在的防禦性斷言，
  兩次的擷取邏輯不同；而且 3 題的樣本小到單題翻面就是 33 個百分點。
  這個對照拿來說明「同一份 golden 可以換模型重考」很夠，拿來當精確的
  模型能力量測則不夠——想要可信的數字，得擴題數並用同一版斷言重跑兩邊。）
- 想加碼：把 `promptfooconfig.local.yaml` 的模型換成 `qwen2.5:3b` 再跑一次
  （workflow 會照 config 裡寫的模型名去 pull，改一個地方就好；3b 比較慢，
  CPU 推論多等幾分鐘是正常的）。

> 歷史註記：本關最初用 GitHub Models 免費推論（2026-07-30 已退役）。
> golden set 與 provider 解耦，題目與 prompt 一字未改，斷言要驗的東西也一樣
> （寫法則改成 try/catch＋從輸出擷取 JSON＋可選鏈存取，好讓小模型的殘缺
> 輸出判 Fail 而不是拋 Error）；改的是 provider 設定與模型佈建——平台會死，
> eval 資產不會。
