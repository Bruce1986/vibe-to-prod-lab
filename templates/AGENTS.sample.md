# <專案名稱> — AI 協作規範（AGENTS.md 範本）

<!--
使用方式（Usage）：
1. 複製本檔到你的 repo 根目錄，改名為 AGENTS.md。
   （Style／Review 兩節要貼的原文在本課程 repo 的
    templates/coding-review-principles.md 與 templates/pr-checklist.md；
    這兩個相對路徑離開本 repo 就不存在，請一併複製走或先把內容貼進來。）
2. 逐節把 <> 佔位符換成你專案的實況；用不到的節直接刪掉。
   （佔位符跨行沒關係：HTML 標籤必須以 ASCII 字母開頭，`<` 後接中文
    會被 CommonMark 當一般文字轉義顯示，不會被當成標籤而隱藏。）
3. Claude Code 使用者另建一個 CLAUDE.md，內容只要一行：@AGENTS.md
   （VS Code Copilot 會直接讀 root 的 AGENTS.md，不用額外設定；
    Windows 環境不要用 symlink——會被 git checkout 成純文字檔而靜默失效。）
4. 範本放在 templates/ 且不叫 AGENTS.md，是為了避免被各家 coding agent
   自動當成本 repo 的規範載入；複製到你的專案後改名即可生效。
-->

## 專案是什麼（What）

<一句話說清楚這個 repo 是什麼、給誰用、目前狀態。
 AI 讀不懂專案目的時，生成就會跑偏。>

## 結構地圖（Map）

<列出重要目錄與各自職責，AI 才不會把檔案放錯地方。例：>

```
src/        <主程式>
tests/      <測試；新功能的測試放這>
docs/       <文件>
```

## 常用指令（Commands）

- 測試：<例：`python -m pytest -q`>
- Lint／格式化：<例：`ruff check .`>
- 本機啟動：<例：`npm run dev`>

## 工作守則（Rules）

1. 改程式**一定要新增或更新對應測試**，跑 <測試指令> 全綠才算完成。
2. 不要新增相依套件，除非使用者明確同意。
3. Commit 訊息：<語言與格式，例：正體中文祈使句，一個 commit 一個意圖>。
4. <專案特有的地雷：不能動的檔案、刻意如此的設計、已定案勿翻案的決策。
   這一節越誠實，AI 幫倒忙的機率越低。>

## 程式碼撰寫原則（Style）

<貼上本課程 `templates/coding-review-principles.md` 的「程式碼撰寫原則」十條，
或放你團隊 style guide 的連結。>

## Code Review 原則（Review）

<貼上本課程 `templates/coding-review-principles.md` 的「Code Review 原則」八條
（可勾選版見 `templates/pr-checklist.md`：那份依作者／reviewer 重新分組並補了
課程特有檢查，共 14 項比這八條多，兩者不是一對一對應）。
重點：AI 生成的 code 用更嚴的標準審。>

## 語言（Language）

回覆與文件使用正體中文（台灣用語）；程式碼識別字與技術名詞維持英文。
