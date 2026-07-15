---
name: course-help
description: 介紹本課程 repo 的地圖、三個 lab 與常用指令。學員剛 clone、迷路、或不知道下一步該做什麼時使用。
---

先讀 repo 根目錄的 `README.md` 與 `AGENTS.md`（不要憑印象猜測），然後用正體中文
（台灣用語）簡潔回覆，包含：

1. 一句話說明這個 repo：臺大課程「從 Vibe Coding 到 Production Architecture」
   下午場（Testing & Quality Engineering）的教學 repo，示範應用是珍奶點餐 bot，
   LLM 全部用預錄 fixtures 回放、零 API key。
2. 三個 lab 的位置與目標（`labs/lab1-testing`、`labs/lab2-golden-eval`、
   `labs/lab3-production`），建議照順序做：`/lab1` → `/lab2` → `/lab3`，
   加分關 `/live-eval`。
3. 常用指令：`python -m pytest -q`、`ruff check app tests labs`、
   promptfoo golden eval（見 lab2 README）、`gh workflow run eval-live.yml`。
4. 若學員環境還沒建好，先帶他們完成 `labs/lab1-testing/README.md` 的第 0 步。

回覆保持在半頁以內，重點是讓學員知道「下一步做什麼」。
