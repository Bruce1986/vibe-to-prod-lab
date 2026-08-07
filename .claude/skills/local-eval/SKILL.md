---
name: local-eval
description: 加分關——在 CI runner 上啟動本地小模型（Ollama）跑真 LLM 評測，零 token 零費用，並幫學員解讀結果。
disable-model-invocation: true
---

你負責帶學員打加分關：讓一個真的 LLM（本地小模型 qwen2.5:1.5b，跑在
GitHub Actions 的 runner 上）考同一份 golden 卷——零 API key、零外部帳號、
零費用。全程正體中文（台灣用語）。

步驟：

1. 前置確認：學員的 repo 已 push 到 GitHub（用 template 建立的自己的 repo）。
2. 觸發（擇一）：
   - 有 `gh` CLI：`gh workflow run eval-local.yml`，然後
     `gh run list --workflow=eval-local -L 1` 拿 run id，再 `gh run watch <id>`。
   - 沒有 `gh`：瀏覽器 → repo → Actions → `eval-local` → 「Run workflow」。
3. 等約 3 分鐘（裝 Ollama＋拉模型＋CPU 推論）。
4. 解讀結果（重點）：
   - **這是 monitor 不是 gate**——紅色是資訊，不擋部署。
   - 對照組：雲端 gpt-4o-mini 曾以同一份考卷拿 3/3；1.5B 小模型的常見
     失誤＝幻覺誘餌（跳跳糖）上當、模糊輸入不反問直接瞎猜。
   - 帶學員逐題看：哪一題掛？掛在契約（is-json＋schema）還是語意斷言？
5. 想加碼：改 `labs/lab2-golden-eval/promptfooconfig.local.yaml` 換模型
   （例如 `qwen2.5:3b`）再跑一次，比較同卷分數——這就是 Evaluation
   Pipeline 的日常用法。
6. 歷史註記（學員問起就講）：本加分關原以 GitHub Models 免費推論實作，
   該服務 2026-07-30 全面退役；因為 golden set 與 provider 是解耦的，
   遷移只改了一行 provider 設定——平台會死，eval 資產不會。
