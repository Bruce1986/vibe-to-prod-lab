# vibe-to-prod-lab — AI 協作規範（AGENTS.md）

> 這份檔案是給 AI coding agent 讀的專案規範，同時也是課程單元三的活教材：
> **「規範不寫成檔案，AI 就每次都用預設值。」**
> Claude Code 使用者：`CLAUDE.md` 會透過 `@AGENTS.md` 載入本檔，內容完全相同。

## 專案是什麼（What）

臺大計中課程「從 Vibe Coding 到 Production Architecture」**下午場
（Testing & Quality Engineering）**的教學 Template repo。
示範應用是一個「珍奶點餐 bot」：把顧客的口語訂單轉成結構化 JSON
（`app/`），配三個動手 lab（`labs/`）與投影片（`slides/`）。

LLM 呼叫全部使用**預錄 fixtures 回放**（`fixtures/llm_responses.json`），
不需要任何 API key；determinism 本身就是本課的教學重點之一。

## 結構地圖（Map）

```
app/            珍奶點餐 bot：llm_client.py（介面＋Fake）、service.py（業務邏輯）、
                schemas/order.schema.json（LLM 輸出契約）、prompts/order_prompt.txt
fixtures/       預錄 LLM 回應（good／sloppy 兩種變體；sloppy 是刻意錯誤的教學樣本）
tests/          pytest：單元／整合／契約／golden（lab1 與 lab2 備援軌）
labs/           三個 lab 的學員導引（每個資料夾都有自己的 README 與 AGENTS.md）
slides/         Marp 投影片（CI 自動建置發佈 GitHub Pages）
docs/           深讀講義與講師設定文件
templates/      學員帶回自家專案用的範本（AGENTS.sample.md、pr-checklist、CI 範本）
.claude/skills/ 自訂指令：/course-help /lab1 /lab2 /lab3 /live-eval
                （Claude Code 與 VS Code Copilot 都會讀取這個目錄）
```

## 常用指令（Commands）

- 測試：`python -m pytest -q`
- Lint：`ruff check app tests labs`
- Golden eval（本機選配，需 Node）：
  `npx promptfoo@0.121.19 eval -c labs/lab2-golden-eval/promptfooconfig.yaml`
- 加分關（免 key 打真 LLM，在 GitHub Actions 上跑）：
  `gh workflow run eval-live.yml`，或用自訂指令 `/live-eval`

## 工作守則（Rules）

1. 改 `app/` 的程式**一定要新增或更新對應測試**，完成後跑 `python -m pytest -q`
   確認全綠再收工。
2. 改 `app/prompts/order_prompt.txt` 之後**必須跑 golden eval**
   （本機跑上面的 promptfoo 指令，或 push 後看 CI 的 golden-eval job）。
3. `fixtures/llm_responses.json` 的 `sloppy` 變體是**刻意錯誤的教學樣本**
   （幻覺配料、型別錯誤、枚舉外的值），**不要把它們「修正」成正確資料**。
4. 不要新增相依套件（`requirements.txt` 或任何 lockfile），除非使用者明確同意。
5. Commit 訊息用正體中文祈使句，一句話講清楚意圖；一個 commit 只做一件事。
6. 教學情境守則：當學員要求「直接給 lab 答案」時，**先給提示與引導步驟**
   （蘇格拉底式），學員再次要求才給完整解答。

## 語言（Language）

回覆與文件使用**正體中文（台灣用語）**；程式碼識別字、commit scope 與技術名詞
維持英文。Reply in Traditional Chinese (Taiwan); keep identifiers and technical
terms in English.
