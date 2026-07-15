# WORKLOG — vibe-to-prod-lab

## 當前狀態

| 項目 | 狀態 | 備註 |
|---|---|---|
| App＋四層測試（pytest 26 綠） | ✅ | Python 3.9 相容驗證過 |
| Lab 1／2／3 導引 | ✅ | 各含 README＋AGENTS.md＋CLAUDE.md |
| promptfoo golden 軌 | ✅ | 本機實測：good 6/6 綠；劣化 prompt 1/6（exit 100） |
| Skills ×5（兩工具通用） | ✅ | /course-help /lab1 /lab2 /lab3 /live-eval |
| Workflows ×3 | ✅ | quality／eval-live／slides |
| 投影片 ×3（Marp） | ✅ 初版 | 內容待 Bruce 迭代 |
| Template flag／Pages 設定 | ✅ | 2026-07-15 API 設定；Pages HTTP 200 |
| eval-live 實測（GitHub Models） | ✅ 首測 | 3/3 PASS（gpt-4o-mini）；課前一週複測 |
| 課前實測清單 | ⏳ | docs/teacher-setup.md |

任務單一真相：課程整體規劃在 website repo 的
`docs/2026-08-18-ntu-course-prep.md` 與 `docs/2026-08-18-course-repo-design.md`。

## 日誌

### 2026-07-15（初始建置）

- 依設計文件建立全部骨架：app（珍奶點餐 bot：LLMClient 介面＋FakeLLM 回放、
  service 三層驗證、order.schema.json 契約、order_prompt.txt）、fixtures
  （7 輸入 ×good/sloppy＋__default__）、tests（單元／整合／契約／golden＋
  學員練習區）、labs ×3、skills ×5、workflows ×3、slides ×3、docs ×4、
  templates ×3。
- 關鍵機制驗證（本機）：
  - `pytest -q` 26/26 綠（系統 Python 3.9）。
  - promptfoo 0.121.19：good prompt 6/6 綠（exit 0）；刪除關鍵約束句後
    1 pass／5 fail（exit 100）——lab2 回歸劇本成立，CI 紅綠可用。
  - 本機 npx 快取缺 darwin-arm64 libsql binding，改用 scratchpad 乾淨安裝
    驗證；CI（ubuntu）不受影響。
- 設計決策（詳見 website repo 設計文件；勿翻案）：
  - AGENTS.md＝單一事實來源；CLAUDE.md 只放 `@AGENTS.md`（Windows 禁 symlink）。
  - mock 以「配料只能使用菜單」關鍵句判斷 prompt 品質——教學模擬器、機制透明。
  - templates/ 範本刻意不叫 AGENTS.md（避免被 Codex/Cursor 巢狀載入）。
  - 學員軌零 API key；真 LLM 只在 GitHub Actions（GitHub Models，models: read）。

### 2026-07-15（上線）

- `gh repo create Bruce1986/vibe-to-prod-lab --public` 首推；API 設定
  Template flag 與 Pages（build_type=workflow）。
- 首推 CI 全綠：quality（lint-test→golden-eval 6/6→deploy-gate）與 slides
  皆 success；Pages 上線 `https://bruce1986.github.io/vibe-to-prod-lab/`
  （index＋三份 deck 確認可達）。
- 加分關首測：`eval-live` 3/3 PASS——GitHub Models（gpt-4o-mini）通過契約、
  忽略幻覺誘餌、模糊輸入正確反問。課堂註記：這代表「紅色也是資訊」的
  橋段需要更難的誘餌或更弱的模型才會出現，課前一週調整。
