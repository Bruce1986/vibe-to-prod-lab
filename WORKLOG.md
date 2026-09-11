# WORKLOG — vibe-to-prod-lab

## 當前狀態

| 項目 | 狀態 | 備註 |
|---|---|---|
| App＋四層測試（pytest 26 綠） | ✅ | Python 3.9 相容驗證過 |
| Lab 1／2／3 導引 | ✅ | 各含 README＋AGENTS.md＋CLAUDE.md |
| promptfoo golden 軌 | ✅ | 本機實測：good 6/6 綠；劣化 prompt 1/6（exit 100） |
| Skills ×5（兩工具通用） | ✅ | /course-help /lab1 /lab2 /lab3 /local-eval |
| Workflows ×3 | ✅ | quality／eval-local／slides |
| 投影片 ×3（Marp） | ✅ v2+ | 13／18／12 張；含講者備忘＋時間配額；案例①②已入 deck 2；待 Bruce 彩排微調 |
| 案例集 docs/case-studies.md | ✅ 定稿 | 六案（07-16 owner 核准；「錯的 base」案依 owner 決策移除）；對照表對齊官方課綱 |
| Template flag／Pages 設定 | ✅ | 2026-07-15 API 設定；Pages HTTP 200 |
| 加分關 eval-local（Ollama） | ✅ 已換引擎 | GitHub Models 7/30 退役→改本地小模型；PoC 1/3、約 3 分鐘、零 token |
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

### 2026-07-16（加分關換引擎：GitHub Models 退役應變）

- **背景**：GitHub Models 官方公告 2026-07-30 全面退役（7/1 changelog、
  7/16 與 7/23 brownout、含既有客戶）——原加分關 eval-live 會在開課前
  19 天死亡。owner 拍板改走本地模型路線。
- **PoC**（分支 `poc/ollama-eval`，已驗證後併回主線）：Ollama qwen2.5:1.5b
  跑在 ubuntu runner 上、promptfoo ollama provider；第一輪 3 題全掛＝
  Ollama 預設輸出上限截斷 JSON（教訓：eval 基礎設施要先驗自己），加
  `num_predict: 512`＋`temperature: 0` 後：**1/3 通過、全程約 3 分鐘、
  零 token 零帳號零費用**；失敗的兩題＝幻覺誘餌上當、模糊輸入瞎猜——
  與雲端 gpt-4o-mini 的 3/3 形成同卷對照，「紅色也是資訊」內建。
- **主線重構**：eval-live.yml／promptfooconfig.live.yaml 移除；新增
  eval-local.yml＋promptfooconfig.local.yaml＋tests.small.yaml（原
  tests.live.yaml 改名重註解）；skill `/live-eval` → `/local-eval`；
  README／AGENTS.md／CLAUDE.md／lab2 README＋AGENTS／deck 2（案例①加映、
  訃聞頁擴為雙訃聞、Lab 2 卡）／teacher-setup 全數同步。
- **設計定位**：eval-local 是 **monitor 不是 gate**——紅色是資訊、不擋
  部署，與案例 6（known-failing monitor）同構；GitHub Models 退役史
  保留為教材（provider 抽象讓 golden 題目與 prompt 免改；實際出力的是
  provider 設定、生成參數、模型佈建與斷言寫法加固——不是「只改一行」，
  這點在 docs/02-llm-quality.md 已誠實寫明，兩處說法須一致）。

### 2026-09-11（加分關的結果判讀：把「沒作答」與「答錯」分開）

- **問題**：eval-local 原本用「Ollama daemon 還活著」＋「output.json 存在
  且能 parse」兩道判斷來區分基礎設施故障／設定錯誤／模型答錯。**實測推翻
  第二道**（promptfoo 0.121.19，架一個對 `/api/tags` 回 200、對 `/api/chat`
  回 404 `model not found` 的假 Ollama）：promptfoo 正常結束（exit 100）並
  寫出完全合法的 output.json，三筆 `response.output` 全是空字串，
  `stats.errors` 是 **0**、`failureReason` 是 ASSERT。於是整輪落進成功分支，
  摘要印出「🏠 eval-local 完成」並複述「雲端 gpt-4o-mini 曾拿 3/3」——
  讀者只會看到「小模型 0/3」，而真相是模型一題都沒答。
- **順帶推翻的直覺修法**：「改成去找 error／failureReason=ERROR 的結果列」
  在這個狀態下是假守門（那個計數就是 0）。分得出來的訊號只有一個：
  **沒有任何一筆拿到非空的模型輸出**。這條也寫成突變測試釘住。
- **修正**：判讀抽成 `labs/lab2-golden-eval/summarize_eval.js`（workflow 的
  run block 只有真的在 CI 跑一次才會執行，寫錯沒有守門會紅），新增
  `tests/test_eval_summary.py` 用兩份 **promptfoo 實跑出來的原始 output.json**
  兩側都驗；摘要同時改成報出「本次成績 X/N」而不是只複述歷史對照，並把
  lab README 那段誠實但書一併帶進摘要。
- **另修**：評測指令改用 `timeout 480` 自己控時。step 層的 `timeout-minutes`
  先觸發時 GitHub 會直接砍掉整個 run block，精心分層的摘要一行都不會執行
  ——那正是本檔在 job 層特別提防、卻沒有防到這一層（最慢、最可能吃滿時間的
  CPU 推論）的同一種失效。逾時另有專屬摘要。
- 驗證：pytest 61 綠（原 48 ＋ 新 13）、`ruff check app tests labs` 乾淨；
  七個突變（拿掉沒作答判斷／成績寫死 3/3／改用 ERROR 列／空字串算作答／
  workflow 不呼叫判讀／拿掉自控 timeout／timeout 調到比 step 還長）全部致紅。
