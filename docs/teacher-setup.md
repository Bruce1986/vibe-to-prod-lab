# 講師設定與課前檢查（Bruce 用，學員可忽略）

## Repo 一次性設定

- [x] 建 repo：`Bruce1986/vibe-to-prod-lab`（public，2026-07-15）
- [x] Template repository flag（2026-07-15 由 API 設定）
- [x] Pages Source＝GitHub Actions（2026-07-15 由 API 設定）
- [x] `slides` workflow 首跑成功，Pages 上線（HTTP 200）：
      `https://bruce1986.github.io/vibe-to-prod-lab/`
- [ ] （可選）About 欄位補課程說明與 Pages 連結

## brucejhang.com 鏡像投影片

1. 到 Actions → 最新一次 `slides` run → Artifacts 下載 `slides-html`
2. 解壓後放進 website repo（建議路徑
   `tw/topics/brucelectures/vibe-to-prod/`，含 index.html 與三份 deck）
3. 站內連結加到 lectures.html 的「軟體品質與工程實務」區
4. 記得跑 website repo 的 `npm test` 再 commit

## 課前一週實測清單（8/11 前）

- [ ] 最新版 VS Code＋Copilot：clone 後零設定體驗
      （AGENTS.md 生效？`/lab1`～`/live-eval` skills 出現在 `/` 選單？）
- [ ] Claude Code：`@AGENTS.md` 橋接與 skills 觸發
- [ ] Windows 實機：venv＋pytest；Phoenix `pip install arize-phoenix` ＋
      `phoenix serve`（含 6006 port 防火牆）
- [x] `gh workflow run eval-live.yml` 首測（2026-07-15）：**3/3 PASS**，
      gpt-4o-mini 連幻覺誘餌都正確忽略——課前一週再複測一次（模型清單會變動），
      並考慮加一題更難的誘餌，讓「紅色也是資訊」的橋段有戲唱
- [ ] HHEM／LettuceDetect 模型在講師機預下載快取；MiniCheck 770M CPU
      延遲實測（太慢就降級為投影片）
- [ ] promptfoo 0.121.x 是否有 breaking change；必要時調 pin 版本
- [ ] 全班同時 push 的 Actions 併發實測（各自 repo 各自額度，預估最壞排隊 1–2 分）

## 課堂節奏對照（13:20–16:10）

時間表詳見 website repo 的 `docs/2026-08-18-ntu-course-prep.md`；
三段講授對應 `slides/01..03`，三個 lab 對應 `labs/lab1..3`，
第三次休息（15:55–16:05）是彈性緩衝，16:05–16:10 結尾。

## 已知設計決策（勿在課前翻案）

- mock provider 以關鍵句「配料只能使用菜單」判斷 prompt 品質——教學模擬器，
  機制對學員透明公開；真模型驗證走 `/live-eval`。
- 學員軌全部零 API key；需要真 LLM 的環節只放在 GitHub Actions（GitHub Models）。
- `templates/AGENTS.sample.md` 刻意不叫 AGENTS.md 且放深一層——
  避免被任何 coding agent 自動載入。
