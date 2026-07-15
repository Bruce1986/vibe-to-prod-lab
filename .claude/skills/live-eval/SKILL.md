---
name: live-eval
description: 加分關——觸發 GitHub Models 免 API key 的真實 LLM 評測（eval-live workflow），並幫學員解讀結果。
disable-model-invocation: true
---

你負責帶學員打加分關：用 GitHub Models（免 API key）對真 LLM 跑同一套契約
與 golden 斷言。全程正體中文（台灣用語）。

步驟：

1. 前置確認：學員的 repo 已 push 到 GitHub（用 template 建立的自己的 repo，
   不是原始教材 repo）。
2. 觸發方式（擇一）：
   - 有 `gh` CLI：`gh workflow run eval-live.yml`，然後
     `gh run list --workflow=eval-live.yml -L 1` 拿到 run，再 `gh run watch <id>`。
   - 沒有 `gh`：引導學員開瀏覽器 → repo → Actions → `eval-live` →
     「Run workflow」按鈕。
3. 完成後用 `gh run view <id> --log`（或網頁）抓 promptfoo 的結果表格，
   幫學員解讀：
   - 真 LLM 的輸出過了 `order.schema.json` 契約嗎？
   - 三筆測資（基本訂單、幻覺誘餌、模糊輸入）各自的表現？
   - **紅色不是失敗**——是「AI 輸出的不可預測性被量測到了」，
     這正是課程單元二存在的理由。
4. 提醒：GitHub Models 免費層 rate limit 低，短時間內不要連續觸發；
   一個下午跑 1–2 次就夠。
5. 若 workflow 因 rate limit 或模型下架而失敗，向學員說明這也是真實世界的
   一課（外部依賴的存續風險），並記下錯誤訊息回報講師。
