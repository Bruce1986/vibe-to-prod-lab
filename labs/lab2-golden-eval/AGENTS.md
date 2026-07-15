# Lab 2 — AI 協作規範（Golden Dataset 與 Prompt Regression）

本資料夾是課程 Lab 2。上層總規範見 repo 根目錄的 `AGENTS.md`。

## 規則

1. `mock_provider.js` 與 `app/llm_client.py` 共用「配料只能使用菜單」這個
   prompt 品質關鍵句——**兩邊要改就一起改**，並同步更新兩份 README 的說明。
2. 幫學員加 golden case 時，三個地方要一致：`fixtures/llm_responses.json`、
   本資料夾 `tests.yaml`、（建議）`tests/golden_cases.json`。
3. 改完 prompt 或測資後，主動建議跑 golden eval（本機 promptfoo 或 push 看 CI）。
4. `promptfooconfig.live.yaml` 只在 GitHub Actions 跑（需要 GITHUB_TOKEN 與
   models: read），不要嘗試在本機直接執行它。
5. 回覆使用正體中文（台灣用語）。
