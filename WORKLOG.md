# WORKLOG — vibe-to-prod-lab

## 當前狀態

| 項目 | 狀態 | 備註 |
|---|---|---|
| App＋四層測試（pytest 26 綠） | ✅ | Python 3.9 相容驗證過 |
| Lab 1／2／3 導引 | ✅ | 各含 README＋AGENTS.md＋CLAUDE.md |
| promptfoo golden 軌 | ✅ | 本機實測：good 6/6 綠；劣化 prompt 1/6（exit 100） |
| Skills ×5（兩工具通用） | ✅ | /course-help /lab1 /lab2 /lab3 /live-eval |
| Workflows ×3 | ✅ | quality／eval-live／slides |
| 投影片 ×3（Marp） | ✅ v2+ | 13／18／12 張；含講者備忘＋時間配額；案例①②已入 deck 2；待 Bruce 彩排微調 |
| 案例集 docs/case-studies.md | ✅ 定稿 | 六案（07-16 owner 核准；「錯的 base」案依 owner 決策移除）；對照表對齊官方課綱 |
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

### 2026-07-15（投影片 v2 迭代）

- 三份 deck 全面加深（13／17／12 張，本機 marp-cli 建置驗證通過）：
  - 每頁加 **講者備忘**（HTML 註解＝Marp presenter notes）：時間配額、
    要落地的重點、demo 切換動線、巡場注意事項。
  - 塞入 repo 實檔片段：test_service 斷言、order.schema.json 枚舉、
    tests.yaml golden case、quality.yml golden-eval job、log_demo 的 JSONL。
  - 單元二 12→17 張（重頭戲）：新增「真實案例①AI reviewer 把現役 model
    判幻覺」「初判 high 過半陣亡」兩頁去識別化第一手案例（無 repo 名／
    無程式碼，Bruce 可否決）、「安全網收網流程圖」「最小起步法三步」。
  - 統一 footer、字級調投影機友善（section 26px、code 0.72–0.85em）。
- 版面爆版檢查列入課前彩排項（本機瀏覽器 pane 故障未逐頁截圖）。

### 2026-07-15（上線）

- `gh repo create Bruce1986/vibe-to-prod-lab --public` 首推；API 設定
  Template flag 與 Pages（build_type=workflow）。
- 首推 CI 全綠：quality（lint-test→golden-eval 6/6→deploy-gate）與 slides
  皆 success；Pages 上線 `https://bruce1986.github.io/vibe-to-prod-lab/`
  （index＋三份 deck 確認可達）。
- 加分關首測：`eval-live` 3/3 PASS——GitHub Models（gpt-4o-mini）通過契約、
  忽略幻覺誘餌、模糊輸入正確反問。課堂註記：這代表「紅色也是資訊」的
  橋段需要更難的誘餌或更弱的模型才會出現，課前一週調整。
- 作者身分修正：首兩個 commit 誤用 global 的公司信箱（顯示為 homee-brucejhang），
  已 filter-branch 改寫為 `8408455+Bruce1986@users.noreply.github.com` 並
  force push（當時無其他 clone）；本 repo 與 website repo 均已設 local
  user.name／user.email 防再犯。教訓：**憑證帳號≠commit 作者**，
  多身分機器開新 repo 首 commit 前先查 `git config user.email`。

### 2026-08-21（templates/ 補課堂講義十條＋八條）

- `templates/AGENTS.sample.md` 的 Style／Review 兩節原本寫「貼上課程講義的十條／
  八條原則」，但 repo 裡沒有這份講義——引用是懸空的。改法：把原則移植成
  `templates/coding-review-principles.md`（來源為 website repo 的備課文件
  `docs/2026-08-18-ntu-course-prep.md` 第 5、6 節，owner 已定稿），兩節改指實檔。
- 同步四處引用：根 `AGENTS.md` 結構地圖、`README.md` 的 repo 地圖與「搬回團隊」
  FAQ、`slides/03-production-quality.md` 的「帶回團隊的三件禮物」→ 四件。
  （前一版只改了 AGENTS.md，README 與投影片還停在三項，學生照著帶回會漏掉新檔。）
- `AGENTS.sample.md` 的 Usage 步驟 1 補一句：`templates/…` 這些相對路徑離開本 repo
  就不存在，要一併複製或先把內容貼進來。
- 已知未解（留給 owner 裁決，非本 PR 範圍）：
  - 十八條原則目前有三份人工同步的副本（備課文件、`coding-review-principles.md`、
    `pr-checklist.md` 的衍生版），CI 沒有任何機制防漂移。已在兩份 templates 互相
    標註「改動請同步」，但沒有自動守門。
  - `quality.yml` 的三關是三個 job：`lint-test`（ruff 與 pytest 同一關）、
    `golden-eval`、`deploy-gate`；`slides.yml` 把 markdown 交給 marp 建成 HTML、
    產索引頁與鏡像用 artifact 後部署 Pages，全程不檢查內容對不對。全 CI 沒有
    markdown lint 或連結檢查，文件斷鏈不會被擋下。
- 第 4 輪（Opus tracer）修掉前幾輪自己寫錯的三句話：`pr-checklist.md` 與
  `coding-review-principles.md` 都把前者說成「那八條的精簡版」，但它其實有 14 項，
  比八條**多**不是精簡（當時順手寫的組成拆解加不起來，第 7 輪已重算）；
  「兩份 templates 互相標註要同步」當時只做了單向（只有 pr-checklist 那一邊），
  已補齊反方向；WORKLOG 原寫「`quality.yml` 只跑 ruff check」也不實——它還跑
  pytest 與 golden-eval，正是本課程投影片拿來當「三關品質管線」教材的那份。
- 第 5 輪（學員實作／逐條事實查證／資訊架構三個視角）三條，都是本次改動自己帶進來的：
  - 「精簡版」的說法上一輪只在 `coding-review-principles.md` 與 `pr-checklist.md`
    改掉，`AGENTS.sample.md` 那句是同一次改動新加的、仍寫「可勾選的精簡版」，於是
    三份 templates 對同一件事各自表述。已一併改成「可勾選版……共 14 項比這八條多」。
  - `coding-review-principles.md` 開頭指向 `AGENTS.sample.md` 的相對連結，在讀者照
    `AGENTS.sample.md` 自己的步驟 1「複製到 repo 根目錄改名為 AGENTS.md」之後就指不到
    檔案——正是本 PR 要修的那類懸空引用，反向重製了一份。已改成不可點的路徑說明。
    （當時判定另兩條 `pr-checklist.md` ↔ `coding-review-principles.md` 的互指「不受
    影響，那兩檔是整批複製、不改名」——**第 6／7 輪證明這個判定是錯的，已改**。）
  - 投影片講者備忘的秒數對不上：件數從三改四時，「三個檔案各 30 秒」（＝90 秒，剛好
    是同一行標的 1.5 分）改成「四個檔案各 20 秒」只剩 80 秒。已補上末段 Template
    說明的 10 秒，讓算式回到 1.5 分。
  本輪查證屬實、勿重審：撰寫十條與 Review 八條對備課文件 §5/§6 逐行比對仍 100% 逐字
  相符（比對程式做過反向突變，改一個詞即轉紅）；`pr-checklist.md` 實數 8＋6＝14 項；
  `templates/` 四個檔案與 README／AGENTS.md／投影片三處清單一致；`labs/*/AGENTS.md`、
  `.claude/skills/*/SKILL.md`、`.github/copilot-instructions.md` 本來就不列舉 templates
  內容，不需跟著改。
- 第 6／7 輪（教學時間表／語言用詞／範圍與紀錄誠實性三個視角，另加一次 Codex 獨立審）
  五條全修：
  - 上面那條「`quality.yml` 三關」在第 4 輪被改寫時**改錯了**：三關是三個 job
    （`lint-test`／`golden-eval`／`deploy-gate`），不是 ruff／pytest／golden-eval
    三項——把 lint-test 拆成兩關又漏掉 deploy-gate，正好與同一個 PR 也動到的
    `slides/03-production-quality.md`（第 38–44 行的 `quality.yml` 節錄，本 PR 未改
    那幾行）自相矛盾；順帶「slides.yml 只涵蓋 Python 與 prompt」也不對，它處理的
    是 markdown。兩處已改。（獨立的 reviewer 與 Codex 各自抓到同一條。）
  - 「14 項」的組成拆解一直加不起來：原寫「八條重新分組＋撰寫十條第 1、9 條＋兩項
    課程特有」＝12，卻宣稱 14；`coding-review-principles.md` 那份還同時寫「第 7 條
    沒有對應項」，實際只剩 11。逐項比對後重寫成加得起來的版本：Review 八條攤成 8 項
    （第 5 條拆成「幻覺 API」與「更嚴標準」，第 7 條無對應項）＋撰寫十條第 1、4、9 條
    共 4 項（第 4 條在作者與 reviewer 兩區各一項）＋課程特有 2 項＝14。審查當下寫過
    一支比對程式核對「宣稱組成合計＝實際 checkbox 數」、並反向突變確認任一數字寫錯
    會轉紅——**那是一次性驗證，沒有落地成 CI 守門**（本 PR 是 docs-only，未新增任何
    腳本）；日後改動仍要靠人記得。
    reviewer 區的「邊界條件與錯誤路徑有測到」與 Review 第 5 條的「邊界條件、錯誤處理」
    重疊，歸給撰寫十條第 4 條是兩種可辯護分法之一，已在 `pr-checklist.md` 就地註明。
  - `templates/` 三份檔案之間不再使用相對連結，一律寫成 repo 根目錄起算的路徑：
    `pr-checklist.md` 的用法就是整段貼進 `.github/pull_request_template.md`，一搬
    位置相對連結就斷。第 5 輪只修了指向 `AGENTS.sample.md` 的那一條，當時判定另兩條
    互指「不受影響」是錯的。
  - `AGENTS.sample.md` 的 Usage 把 `pr-checklist.md` 也說成 Style／Review 兩節「要貼
    的原文」，但本文只叫人貼 `coding-review-principles.md`，checklist 是衍生版；已
    改寫。同節引用的章節名補上「簡易」二字，與來源標題的主標一致（沿用 Style 節的
    慣例，略去「（AI 時代版）」）。
  - `coding-review-principles.md` 的「修改請與來源文件同步」對複製走的人不可能履行
    （來源檔在講師的另一個 repo）。已限定為「給教材維護者」，並明講複製走的人不受
    此約束。
  留給 owner（本輪查到、但不宜由審查逕自決定）：`slides/03-production-quality.md`
  逐頁講者備忘加總 19 分，該單元標的 22 分（line 20「15:16 開講」到 line 177
  「15:38 實作」），差 3 分沒有落在任何一頁。此落差在本 PR 之前就存在（本 PR 未增減
  頁數、也未改動其他頁的分鐘數），要補在開場還是攤進各頁是教學安排，留給講者決定。
