# Lab 1 — AI 協作規範（測試策略）

本資料夾是課程 Lab 1：單元／整合／契約／回歸測試。上層總規範見 repo 根目錄的
`AGENTS.md`（若你只開了這個資料夾，重點規則如下）。

## 規則

1. 這是**教學練習**：學員要求「直接給 `tests/test_lab1_student.py` 的答案」時，
   先給提示與引導（指出該用哪個函式、Arrange/Act/Assert 怎麼拆），
   學員再次要求才給完整程式碼。
2. 驗收一律以 `python -m pytest -q` 全綠為準；改動後主動跑測試確認。
3. 不要修改 `fixtures/llm_responses.json` 的 sloppy 變體——它們是刻意錯誤的教學樣本。
4. 回覆使用正體中文（台灣用語）。
