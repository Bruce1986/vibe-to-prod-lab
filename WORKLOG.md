# WORKLOG — vibe-to-prod-lab

## 當前狀態

| 項目 | 狀態 | 備註 |
|---|---|---|
| App＋四層測試（pytest 全綠，數量見日誌最新一筆） | ✅ | Python 3.9 相容驗證過 |
| Lab 1／2／3 導引 | ✅ | 各含 README＋AGENTS.md＋CLAUDE.md |
| promptfoo golden 軌 | ✅ | 本機實測：good 6/6 綠；劣化 prompt 1/6（exit 100） |
| Skills ×5（兩工具通用） | ✅ | /course-help /lab1 /lab2 /lab3 /local-eval |
| Workflows ×3 | ✅ | quality／eval-local／slides |
| 投影片 ×3（Marp） | ✅ v2+ | 13／18／12 張；含講者備忘＋時間配額；案例①②已入 deck 2；待 Bruce 彩排微調 |
| 案例集 docs/case-studies.md | ⏳ 待 owner 確認 | 六案；對照表對齊官方課綱。⚠️ 本列原記「✅ 定稿（07-16 owner 核准）」，但該說法與檔案內文的「草稿，待講師逐案核准」出自**同一顆 commit `a008d2b`**（建檔那顆），兩者不是獨立佐證，無法由 repo 內部判定——詳見該檔開頭與 2026-09-21 條目⑮ |
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
- **同輪再修三處（錯誤處理視角）**：
  ① `quality.yml` 的 `lint-test` 沒裝 node，而 `tests/test_eval_summary.py`
  與 `tests/test_local_eval_asserts.py` 這兩份（要靠 node 跑「線上那份
  JavaScript」的守門）都用 `skipif` 保護——**本機實測 `env -i PATH=<空目錄>
  pytest <那兩份>` 得到整批 skipped、離開碼 0**，守門一條都沒跑、CI 照樣全綠。
  補上 `actions/setup-node@v4`（與另兩軌同為 22），並新增
  `tests/test_ci_toolchain.py`：CI 上沒有 node 就紅，本機維持可跳過。
  ② eval-local 的「拉取小模型」把 `MODEL=$(sed … config | head -1)` 的
  結果交給 `-z` 判斷，但 GitHub Actions 的 run 預設是 `bash -eo pipefail`，
  config 不存在時 sed 回非零、`set -e` 當場中止，那句友善的 `::error::`
  永遠印不出來（實測：修正前只吐 `sed: …: No such file or directory`，
  修正後吐 `::error::找不到 …`）。改成先檢查檔案存在。
  ③ `summarize_eval.js` 對非物件的結果列會拋 TypeError（崩掉＝step summary
  一片空白），加上防護；`run_summary` 改成不吃 `check=True`，讓 node 的
  stderr 出現在失敗訊息裡——守門自己紅的時候要看得出原因。
- 補記一個自己造的假守門：①的防護剛寫好時，配的兩個測試案例（結果列是
  null／字串）在**拿掉防護後照樣全綠**——它們在「全部沒作答」就先轉彎了，
  根本走不到會崩的算分那段。改成「有作答的列後面混一個 null」才真的致紅。
- **同輪再修三處（接手性視角）**：
  ④ 上一條記錄裡「35 條守門」這個數字**從寫下的那一刻就是錯的**（實際 38，
  因為同一個 commit 又加了 3 個 parametrize 案例）。已把 quality.yml 註解、
  `test_ci_toolchain.py` 與本檔的說法改成不寫死數量——這種會隨 parametrize
  浮動的計數寫進四個地方，等於一次留四句遲早過期的宣稱。
  ⑤ `tests.small.yaml` 的三段掃描器是逐字拷貝，但只有第 1 題被餵過圍欄／
  覆誦範例／未配對引號那些邊角輸入——另外兩份的掃描器等於從沒被考過。
  已把邊角案例補到第 2、3 題，並新增 `test_three_scanners_stay_byte_identical`
  把「三份必須同步」這個原本只存在腦中的契約釘成守門（實測：只改其中一份
  即致紅），tests.small.yaml 的註解也寫明。
  ⑥ 兩份 fixture 只留下指向某台機器暫存沙箱的絕對路徑當線索，等於沒有
  重現方式。已附上 `tests/fixtures/eval_local/fake_ollama.py`（產生那份
  provider-error 原檔用的假 Ollama）與 README 裡可複製貼上的完整步驟，
  並把絕對路徑換成佔位字串（README 寫明只動了這一處與檔名）。
- **同輪 Opus tracer 專審本日三顆 commit，抓到 6 條自造缺陷（全修）**：
  ⑦ **「部分題目沒作答」時把沒答到的算進分母**——3 題裡 2 題沒輸出、1 題
  答對會印成「本次成績 1/3」並與 gpt-4o-mini 的 3/3 並排，正是本日要修的
  那種誤讀，只是縮小成部分題目。改成分母只算真的拿到輸出的題目
  （「1/1（另有 2 筆沒拿到模型輸出，不計分）」）。
  ⑧ **把本次題數內插進固定的歷史事實**：「曾以這 ${total} 題拿 3/3」
  「${total} 題的樣本小到單題翻面就是 33 個百分點」——3/3 與 33 都是寫死的，
  只有分母會動，題數一變就印出捏造的量測。且 promptfoo 的**列數＝題數 ×
  provider 數**（⚠️ 2026-09-21 更正：原本這裡寫「實測：同一份 tests.small.yaml
  配兩個 provider ⇒ 6 列、testIdx 為 [0,0,1,1,2,2]」，但 repo 裡沒有 2-provider
  的原始 output.json，當時的驗證是由既有 fixture 衍生的、不是實跑留底。
  「列數＝題數 × provider 數」與 promptfoo 的文件化行為一致，但本 repo 未留證，
  故撤下「實測」二字）。歷史對照句全部寫死，題數改由 testIdx 去重算，
  題數不是 3 時直接說「沒有可比的對照組」。
  ⑨ 檔頭實測記錄裡「整份檔案裡沒有任何 error 欄位」**是錯的**：三筆都有
  `error`，內容是斷言訊息，跟模型真的答錯時長得一樣——那才是「找 error 列」
  分不出來的真正理由。已改正，並補測試把新說法釘住。
  ⑩ 「全部沒作答」那段無條件說「promptfoo 把每一筆記成斷言失敗」，但
  errors>0（打不到服務）時記的是 ERROR，同段自相矛盾；措辭改成依 errors 分岔。
  ⑪ `test_ci_toolchain.py` 只檢查執行當下 PATH 有沒有 node，**把 quality.yml
  的 setup-node 整段拿掉照樣全綠**——它宣稱要防的回歸它抓不到。改成直接讀
  quality.yml 斷言 lint-test 有 setup-node，且各軌 node 版本一致。
  ⑫ fixture README 的重現步驟產不出庫裡那份 `output_answered.json`
  （description／providers 對不上）。已照文件步驟**重新產生**該 fixture，
  並實測「照 README 跑出來的 `config` 區塊與庫裡兩份逐字相同」。
- 本輪突變六個（分母含沒作答／題數內插回對照句／不分 errors 同一句話／
  題數用列數不去重／拿掉 setup-node／兩軌 node 版本不一致）全部致紅；
  pytest 78 綠 1 skip、ruff 乾淨。

### 2026-09-21（排程班第 8／9 輪：把「沒量到的東西」從摘要與紀錄裡清掉）

- 第 8 輪（三 lens：迴歸審 720f5d5／測試品質突變／不看 diff 全文通讀）：
  ⑬ `summarize_eval.js` 的 `countDistinct()` 對缺鍵的列用 `#index` 當 key，
  每列各成一組。單一 provider 時剛好等於題數、看不出問題；**2 個 provider
  就把 3 題 ×2 的 6 列報成「6 題」**，並因 6 ≠ 3 連帶把對照組改印「本次是
  6 題」——一個憑空捏造的量測，講得跟真的一樣，正是這支摘要存在的理由換了
  個觸發點。改成回傳 `{count, complete}`，不完整時改口「無法回推題數」並
  停掉對照組；列數（實際數得出來）照報、成績（逐列算）不受影響。
  ⑭ `test_ci_toolchain` 的 `"actions/setup-node" in body` 純子串比對會被
  step 名稱騙過（reviewer 實測誤觸：step 取名含該字串時假綠）。改比對
  `uses:` 欄位。
- 第 9 輪（Opus 對抗性 tracer，專打第 8 輪自己的修正）：
  ⑮ 🔴 **撤回第 8 輪對 `docs/case-studies.md` 的「定稿」判定**。第 8 輪宣稱
  「repo 內部證據足以判定、不再需要 owner 裁決」，依據是 commit `a008d2b`
  的標題與 `WORKLOG.md` 的「✅ 定稿」。但 `a008d2b` 正是**建檔那一顆**，且
  它**同一次寫入**同時寫下「定稿（owner 核准）」與內文的「草稿，待講師逐案
  核准」——兩份「互相佐證」是同一個作者、同一顆 commit，不是獨立來源。
  已退回「待 owner 確認」並如實記下兩種說法並存。
  ⑯ `providersKnown` 整套零覆蓋（拿掉它 81 passed 全綠），補測試。
  ⑰ 第 8 輪撤掉的那句「實測」只改了 docstring，同一句話在本檔還活著（見
  ⑧ 的更正）。⑱ 第 8 輪補的出處「AGENTS.md『未查證的推測不進永久紀錄』」
  在本 repo 的 AGENTS.md 裡查無此條——寫下查不到的出處，正是那句話要防的事。
  ⑲ 跳脫引號案例只餵第 1 題，另外兩份掃描器仍零覆蓋，各補一筆。
  ⑳ 新測試五條斷言有三條空轉（換個措辭講出捏造的題數仍全綠），改成語意斷言。
- 本輪突變全部致紅（缺 testIdx 冒充題數／缺 provider 冒充 provider 數／
  註解掉 setup-node 的假綠／引號 YAML 的假紅／三份掃描器的跳脫邏輯）；
  pytest 84 綠 1 skip、ruff 乾淨。
- ⚠️ 仍待 owner：`docs/case-studies.md` 的定稿與否；`docs/teacher-setup.md`
  「課前一週實測清單（8/11 前）」下的兩條未勾待辦（2026-08-16 加入，晚於
  自標期限、早於開課日 08-18 兩天，全 repo 查無「下學期」字樣，證據傾向
  過期遺忘但非決定性）；`.claude/skills/local-eval/SKILL.md` 的「只改了
  一行」與本 repo 其餘五處的誠實版本牴觸（owner 第 3 輪已裁示本次不動）。

### 2026-09-24（排程班第 10 輪：clean pass 確認，＋兩條學員路徑的缺口）

- 本輪的指定任務是 clean pass 確認，不是再開新改動。對第 9 輪的八項宣稱逐一
  做突變複驗，**七項完全成立、無迴歸**〔2026-10-11 更正：其中 `multi` 那一項
  事後查出不成立，實為六項，見該項的括號與 ㉟〕：`uses:` 正則（整行註解→紅；雙引號／
  單引號／無空白／改縮排／行內註解→全綠，即假紅已關）、`providersKnown` 新
  守門（退回 `providers>1` → 1 failed）、`multi` 改用 `rows.length !== questions`
  （單 provider＋repeat 2 會印出「共 6 筆結果」〔**2026-10-11 更正：對 promptfoo 實跑的
  `--repeat 2` 輸出，這句不成立，見 ㉟**〕；單 provider
  單次仍不多印，沒有新假紅）、三份掃描器的跳脫案例（只砍第 1／第 2／第 3 份各自都紅）、
  WORKLOG 與 docstring 的「實測」字樣已撤且無第三處殘留、AGENTS.md 出處已改
  成不指名、`docs/case-studies.md` 與本檔狀態表的措辭一致且全 repo 無第三處
  還寫「定稿」。第 8 輪對 `a008d2b` 的誤判也再次複驗屬實（`a008d2b~1` 查無此
  檔＝建檔那顆，同一顆 commit 同時寫下「定稿」與「草稿」）。
- ㉑ **「各軌的 node 版本應該一致」只掃了 quality.yml**。那句斷言訊息寫「各軌」，
  但 `re.findall` 的對象是 quality.yml 的內文，實際只比對它內部 lint-test 與
  golden-eval 兩個 job。`eval-local.yml`（學員按 `/local-eval` 走的那一軌）與
  `slides.yml` 各自也釘 node 版本，漂移沒有人管——突變實證：把 eval-local.yml
  改成 `node-version: 20`、其餘不動，整份 pytest 仍全綠。已抽成獨立的
  `test_all_workflows_pin_the_same_node_version`，掃 `.github/workflows/` 底下
  所有釘了 node-version 的檔案（新增 workflow 自動納入）。回驗：eval-local 改
  20 → 紅、slides 改 18 → 紅、glob 指到不存在的目錄 → 紅（非恆真），原本那條
  `test_lint_test_job_installs_node` 把 `uses:` 整行註解掉仍 → 紅（未退步）。
- ㉒ `docs/02-llm-quality.md` 對學員承諾的「全程約 3 分鐘」沒有時點。出處是
  2026-07-16 的 PoC 分支（`docs/teacher-setup.md:30` 與本檔 07-16 條目都有標
  日期，只有學員讀的那份沒標），而該數字之後 workflow 又經多輪加固，現在四個
  步驟的 timeout 預算合計 28 分鐘、job 層 35 分鐘，重構後未再計時。已在該處補
  上量測時點與「等第一次正式跑完再回來訂正」。
- pytest 85 綠（新增 1）1 skip、ruff 乾淨。
- ⚠️ 待 owner 的三項與上一輪相同，未新增；另 `.claude/skills/local-eval/SKILL.md`
  也寫著同一個未標時點的「約 3 分鐘」，排程班禁止改該目錄，留給 owner。

### 2026-10-10～11（互動 session：第 11–23 輪，owner 指示續審）

- 第 10 輪後本 PR 因輪數上限停審，這次是 owner 手動指示再審。Codex 對
  `origin/main` 的整份 diff 完整跑了四次（第 11、14、19、23 輪）都無意見；以下是 Claude
  reviewer 與主審實測找到的。輪次對照：㉓–㉖ 第 11 輪、㉗ 第 12 輪、㉘ 第 13 輪、
  ㉙–㉛ 第 14 輪（Opus tracer；它另把 ㉓–㉘ 的實測敘述逐條重跑，全部重現）。
  第 15 輪沒有新條目，是回頭修 ㉙ 與 ㉛ 在第 14 輪修得不完整的地方（寫在該兩條內）。
  ㉜–㉞ 第 16 輪（另有一處 ㉙ 的補修，同樣寫在 ㉙ 內）。第 17 輪只改了 ㉝ 的一句兜底訊息。
  ㉟–㊱ 第 18 輪（第二次 Opus tracer；它把 ㉙–㉞ 的回驗逐條重跑，全部重現）。
  Codex 第 18 輪撞到用量上限沒有跑完，不算一次審查。
  第 19 輪只改本檔的三處敘述（第 10 輪條目的合計、㉝ 的句子結構、下方清單的一條）。
  第 20 輪是確認輪，無發現。第 21 輪改了兩句摘要文字：它們叫讀者看「上方」的
  promptfoo 輸出、調「上面的」timeout，但 step summary 頁面上方沒有那些東西，
  改成指名 job log 與 `eval-local.yml`。
  ㊲ 第 22 輪（第三次 Opus tracer；31 個突變，沒有清單以外值得修的新缺口）。
  第 23 輪沒有改程式，只補上本段漏寫的第 22 輪與 Codex 次數。
- ㉓ **「抽取器失誤會被算進分數」不成立**。`tests.small.yaml` 檔頭用這句話解釋
  為什麼要掃平衡花括號。用 promptfoo 0.121.19 配假 provider 實測：輸出是
  「散文＋正確 JSON」或「```json 圍欄＋正確 JSON」時，`defaultTest` 的 is-json
  先掛、語意斷言過、整題 Fail——整題判定由契約斷言決定，語意斷言抽得準不準
  只改變逐條明細。檔頭已改寫成這個說法。掃描器本身沒有動。
- ㉔ **但書的理由寫錯了對象**。`docs/02`、lab2 README、`summarize_eval.js` 都說
  3/3 與 1/3 不可比是因為「擷取邏輯不同」；依 ㉓，擷取不改變整題判定。實測到
  會讓整題判定不同的是：誘餌題若模型回「反問」（合法、符合 schema、沒有
  items），舊單行斷言拋 TypeError 整題 Fail，新斷言判 Pass。三處改成「斷言寫法
  不同」，`docs/02` 另寫出這個例子。**這只是一種實測到的差異，沒有窮舉。**
- ㉕ 誘餌題的斷言補兩筆案例：跳跳糖排在合法配料後面（突變 `toppings[0] ===`
  → 這筆紅；拿掉這筆 → 該突變全綠）、回反問沒有 items（突變拿掉可選鏈 → 這筆紅）。
- ㉖ `slides/02` 的「同一份考卷：1/3 對 3/3」補「非受控對照」，講者備忘加但書；
  README 的「斷言要驗的東西也一字未改」改成「也沒變」；本檔狀態表的
  「pytest 26 綠」是 main 上的數字，改成不寫死。
- ㉗ **兩份測試在非 UTF-8 locale 下有 17 條會紅**。`subprocess.run(text=True)`
  沒指定編碼，會用系統 locale 解 node 印出的 UTF-8。以 `LC_ALL=C PYTHONUTF8=0
  PYTHONCOERCECLOCALE=0`（locale 編碼變成 US-ASCII）重現：修正前 17 failed／
  42 passed（紅的都在 `test_eval_summary.py`，要解 node 印出的中文），補上
  `encoding="utf-8"` 後 59 passed。Windows 中文版（cp950）是同一條路徑，
  **但沒有在 Windows 上實跑**。
- ㉘ **「逐題看掛在契約還是語意斷言」在 Actions 頁面上做不到**（第 13 輪，反方
  論證視角）。`.claude/skills/local-eval/SKILL.md` 第 4 步這樣引導，㉓ 改寫的
  檔頭原本也拿它當掃描器的用途。實跑 promptfoo 0.121.19（workflow 同樣的
  `--no-progress-bar -o output.json`）：job log 的表格每題只有 `[PASS]`／`[FAIL]`
  加模型原始輸出，不印是哪一條斷言掛；`summarize_eval.js` 只報總分；workflow
  沒有上傳 `output.json`。逐條結果只在 runner 上那份 `output.json` 裡，run 結束
  就沒了。本輪只把 `tests.small.yaml` 檔頭改成如實描述，**機制沒有補**——要補
  有兩條路，都是新功能，留給 owner 決定：(a) `summarize_eval.js` 多印一段逐題
  明細（讀 `gradingResult.componentResults`，要一併補測試）；(b) workflow 用
  `actions/upload-artifact` 上傳 `output.json`。SKILL.md 那一步在補之前照做不到。
- ㉙ **學員照 lab2 README 加第 4 題會把主線弄紅**。README 引導「想讓小模型也考
  你那題，把它一併加進 `tests.small.yaml`」，但 `test_extracted_three_assertion_bodies`
  釘死「剛好 3 段」，掃描器一致性那條也對每一段都要求有掃描器。照現有三題的
  `value: |` 寫法加一題 → lint-test 紅，golden-eval 與 deploy-gate 都 `needs:` 它。
  第 14 輪先改成「至少 3 段、只比前三段」，第 15 輪的 reviewer 實測出那只在
  新題加在檔尾時成立（插在最前面 17 failed、插在第 2 題後 7 failed，訊息只有
  `assert False is True`）。改成用題目的 `description` 認那三題、不看順序。
  回驗：新題加在最前面／第 2、3 題之間／檔尾 → 三種都綠；第 3 題改成單行
  `value:` 或第 2 題改名 → 紅，訊息指名是哪一題；只改第 2 份掃描器 → 紅；
  ㉕ 的 `toppings[0]` 突變 → 仍紅。第 16 輪再補一處：新題若不是以
  `- description:` 開頭（例如 `- vars:` 開頭），它的斷言會被記到上一題名下、
  紅在「該題應恰有一段，實際 2 段」。剖析器改成遇到行首 `- ` 就清掉題名
  （回驗：檔尾加一題 `- vars:` 開頭的 → 綠）。
- ㉚ **摘要每次都印寫死的「主線 golden 軌為 6 題」**，而 lab2 第 4 步就是要學員在
  `tests.yaml` 加題——加完之後學員自己 repo 的摘要仍說 6 題。`summarize_eval.js`
  不讀 `tests.yaml`，改成不報數字（「主線 golden 軌的題目在 tests.yaml」）；
  `test_eval_summary.py` 原本為了那句寫死的話要先剔字串再檢查，一併拿掉。
  README／docs／workflow 註解裡對範本的靜態描述「6 題」沒有動。
- ㉛ **fixture 重產步驟會留下一個佔住 11434 的假 Ollama**。`fake_ollama.py` 是
  `serve_forever()`，README 與檔頭都只寫 `… &`，沒有任何一步收掉它；機器上若本來
  有真 Ollama，假的綁不上、promptfoo 會打到真的，步驟也沒有檢查。補上先探埠、
  記 PID、確認回的是 `{"models": []}`、產完 `kill`。「起→探→kill」那段在本機
  實跑過（kill 後埠關閉）；整段重產 fixture 沒有重跑。第 15 輪再補兩處：起了之後
  先 `sleep 1` 再探（否則 `curl -s` 搶在綁埠之前、什麼都不印）；`<此目錄>` 這個
  佔位符在前面已經 `cd` 走之後指不到東西，改成步驟 0 先記下的 `$REPO`。
  這兩處是讀碼改的，改完沒有再實跑。
- 以下 ㉜–㉞ 都在 `eval-local.yml` 最後一步與 `summarize_eval.js` 的銜接處。驗證
  方式：把那一步的 `run:` 抽出來，用替身的 `npx`／`curl`／`timeout` 在本機
  `bash -eo pipefail` 下跑九種組合，看 step 離開碼與 step summary。**這是本機
  bash 3.2 配替身指令，不是在 GitHub Actions 上實跑。**
- ㉜ **全過時 daemon 剛好已死，會印「未完成——基礎設施故障」而 step 是綠的**。
  探測 daemon 那個分支原本對所有非 124 的離開碼都生效，包括 0。改成只在評測
  非零時才探測。回驗：`0＋daemon 死` → 摘要「完成」、step 0；`100＋daemon 死`
  → 仍報基礎設施故障、step 100。
- ㉝ **判讀程式非零結束會吃掉 promptfoo 的離開碼**。`node summarize_eval.js …`
  在 `bash -e` 下失敗會當場中止，`exit "$EXIT"` 走不到，step 以 node 的離開碼
  結束。而檔頭宣稱的「一律以 0 結束」原本並不成立：`testIdx` 是 `toString` 不可
  呼叫的物件時 `String(key)` 會丟 TypeError（promptfoo 正常不會寫出這種值）。
  兩邊都補：workflow 那行加 `|| echo "::warning::…"`；`summarize_eval.js` 的
  進入點包 try/catch，丟例外時印「未完成——判讀程式自己出錯」並照樣以 0 結束。
  新增 `test_summarizer_crash_is_reported_not_swallowed`，拿掉 try/catch → 它紅。
  回驗：`100＋node 非零` → step 100 並有 warning；`0＋node 非零` → step 0。
  （兜底訊息初版寫「讀 output.json 時丟出例外」，第 17 輪 reviewer 指出讀檔失敗在
  `readResults` 就接住了、走不到這裡，已改成「處理內容時」。）
- ㉞ **promptfoo 以 0／100 以外的離開碼結束、卻留有讀得動的 output.json 時，
  摘要照樣寫「完成」**。在摘要前面多印一行警告。**沒有查證真實的 promptfoo 會
  不會在崩潰前留下這種檔案**——這是照離開碼語意加的防禦，0 與 100 這兩個值
  則是本次實跑看到的（全過 0、有題目沒過 100）。
- ㉟ **摘要對 `--repeat` 的說法是錯的，而且錯了兩輪**。`summarize_eval.js` 的註解
  說 `rows.length !== questions` 這個判準是為了「單一 provider 跑 `--repeat 2`」，
  本檔第 10 輪條目還把「會印出共 6 筆結果」列為複驗成立。promptfoo 0.121.19 實跑
  `--repeat 2`（mock provider）：6 列的 testIdx 是 `0,1,2,3,4,5`，摘要印「6 題
  小樣卷」「本次是 6 題」，沒有「共 6 筆結果」。判準對它宣稱要守的情境不生效。
  本輪**只更正文字**（該註解、第 10 輪條目加註），行為沒有改——workflow 沒有用
  `--repeat`。真要守得用題目本身去重並補一份 `--repeat` 實跑的 fixture，留給 owner。
- ㊱ **現行的 `eval-local.yml` 沒有在 GitHub Actions 上跑過**。`gh run list
  --workflow eval-local.yml` 只有兩筆，都是 2026-07-16 `poc/ollama-eval` 分支 push
  觸發的 PoC 版（兩筆的 conclusion 都是 failure）；現行檔只有 `workflow_dispatch`、
  不在 main 上，合併前觸發不了。`docs/teacher-setup.md` 的課前清單原本只寫「課前
  一週複測」，讀起來像已經測過；改成「首次在 Actions 上實跑驗收」並列出要看什麼。
  **合併後第一件事就是手動跑一次。**
- 第 18 輪順手改的三處小地方：最後一步探測 daemon 的 `curl` 加 `--max-time 10`
  （daemon 接了連線卻不回應時原本會卡到 step 上限，摘要整段消失——這是讀碼推論，
  沒有重現）；離開碼警告的「下面的結果」改成「下面的判讀」；註解的「三種原因」
  補上逾時另外處理。
- ㊲ （第 22 輪，Opus tracer）**Actions 預設的 shell 是 `bash -e`，不是
  `bash -eo pipefail`**：未寫 `shell:` 時沒有 pipefail（07-16 那次 PoC run 的 log
  印的是 `shell: /usr/bin/bash -e {0}`）。`eval-local.yml` 拉模型那步的註解、本檔
  09-11 條目裡同一段「實測」、以及上面 ㉜ 前的說明都以 pipefail 為前提。註解已
  改寫；先檢查檔案存在的守門在兩種 shell 下都正確，行為沒有改。tracer 另在
  `bash -e` 下重跑最後一步的九種組合，結果與 ㉜–㉞ 記的相同。09-11 條目未逐字更正。
- 本條目寫下時全套 pytest 88 綠 1 skip、ruff 乾淨（本機 Python 3.12、node 26）。
- 查過但沒有修、留給 owner 判斷值不值得：
  - 掃描器遇到深度 0 的未閉合 `{`（例如散文「格式 { 如下：」）之後收不到任何
    候選，語意斷言會判 Fail。依 ㉓ 那種輸出整題本來就 Fail，只影響明細。
  - `test_workflow_calls_the_summarizer` 是子字串比對：把呼叫改成 `echo node …`、
    拿掉 `|| EXIT=$?` 或 `exit "$EXIT"`，測試都不會紅（reviewer 突變實測）。
    **10-15 已補（㊴）**：三種改法現在都會紅。
  - `summarize_eval.js` 有幾個分支沒有斷言守著（純空白輸出、讀不到結果檔那條
    路徑的 `診斷：` 那行、provider 只有 id 沒有 label 等，第 11 輪同一位 reviewer
    的突變實測；㉝ 新增的兜底路徑的 `診斷：` 則有斷言）。**10-15**：純空白輸出
    已補（㊵）；provider 只有 id 沒有 label 仍沒有守。
  - `--repeat` 下題數會被高估（㉟）。
  - `.claude/skills/local-eval/SKILL.md` 仍寫「同一份考卷拿 3/3」而沒有但書
    （owner 先前指示該檔不動）。
  - main 在本分支之後替單元一投影片加了一頁，狀態表的「13／18／12 張」合併後
    第一個數字會過期。

### 2026-10-13（排程班第 24 輪起：斷言測試分開記「拋例外」與「回 false」）

- 第 24 輪（Sonnet 三個視角＋Codex）：workflow／summarizer 失敗模式、文件事實查核、
  Codex 都沒有發現；測試品質那道做了 51 個突變。
- ㊳ `tests/test_local_eval_asserts.py` 的 `test_assertion_verdict` 把斷言**拋例外**
  與**回 false** 都記成 Fail。`tests.small.yaml` 檔頭寫的「優雅地 false（Fail）而不是
  拋例外（Error）」因此沒有守門：把第 1 題的 `obj?.items?.[0]?.sweetness` 改成
  `obj.items[0].sweetness`、或把第 3 題的 `obj?.status` 改成 `obj.status`，全套照樣
  88 綠。改成拋例外時直接讓該案例失敗。回驗：同樣兩個突變，修正後分別 5 條、1 條變紅。
  這條守的是檔頭對寫法的要求，不是整題判定：promptfoo 0.121.19 的原始碼把拋例外的
  javascript 斷言同樣記成該條斷言失敗（reason 為 `Custom function threw error: …`；
  只讀了本機 npx 快取裡的原始碼，沒有實跑）。
- 第 27 輪（Opus tracer）更正三處敘述：㊳ 的失敗訊息原本寫「promptfoo 會記成 Error
  而不是 Fail」，與上面那段原始碼相反，已改掉；`tests.small.yaml` 檔頭說掃描器兩個細節
  「都被實際驗證過」，第 2 點（掃完一個候選就把字串狀態歸零）拿掉後現有案例仍全綠，
  已照實改寫；`tests/test_eval_summary.py`「有作答的列後面混一個 null」那筆的註解說
  它測得到崩潰路徑，實測只拿掉 badRow 檢查時它不會紅（被 try/catch 兜底接住），已改寫。
- 其餘存活的突變落在上一節「查過但沒有修」已列的兩類（workflow 的字串比對、
  `summarize_eval.js` 沒有斷言守著的分支），同類的新例子有：拿掉 `-o output.json`、
  拿掉寫入 `$GITHUB_ENV` 的 `MODEL=`、評測改用 `promptfooconfig.yaml`、`timeout 480`
  改 590、`"124"` 改 `"125"`（**10-15**：`-o output.json` 與 `"124"` 兩項已由 ㊴ 補上，
  其餘三項仍存活）；讀不懂的結果檔那幾條測試只比對標題，各個前置檢查拿掉後
  仍綠。沒有修，同樣留給 owner 判斷。
- 本條目寫下時全套 pytest 88 綠 1 skip、`ruff check` 乾淨。

### 2026-10-15（互動 session：owner 指示 GGR fix-loop with Codex，第 28–37 輪）

- Codex 第一輪撞到額度上限，沒有產出任何意見；收斂後（額度恢復）再跑一次最終交叉檢查，
  無意見。其餘各輪都只有 Claude reviewer。
- ㊴ `eval-local.yml`「本地模型評測」那段 run block 的控制流程原本只有子字串檢查。
  新增 `test_eval_step_keeps_promptfoo_exit_code_and_writes_summary`：從 workflow 抽出
  run block，用假的 `timeout`／`curl`／`node`／`npx` 以 `bash -e` 實跑 7 種情境，驗 step
  離開碼等於 promptfoo 的離開碼、step summary 走對分支、判讀程式失敗時 job log 有
  `::warning::`。假 curl 只認 `-f` 且打 `localhost:11434` 的呼叫；假 npx 被直接呼叫就以
  97 結束（避免控時寫法被改掉時測試真的去下載 promptfoo）。PATH 只給替身與
  `/usr/bin`、`/bin`，逾時殺整個行程群組。Windows 本機跳過（WSL bash、CRLF），CI 會跑。
- ㊵ `summarize_eval.js` 的判讀補測試：純空白／null 不算作答、物件／空陣列算作答；
  4 題時不印歷史對照；單一 provider 同一 testIdx 兩列時印出列數。
- ㊶ 部分作答（有幾筆沒拿到輸出）時，原本照印「曾以這 3 題拿 3/3」，與只考到一部分的
  成績並列。改成印「沒有可比的對照組」並講明幾筆裡缺幾筆；標題仍為「完成」不變。
- ㊷ 兩處輸出措辭：讀不懂結果檔的分支原本一律說「沒有產出可解析的結果檔、評測根本沒
  跑完」，但 JSON 合法、結構不對時也走這裡，已改成兩種都成立的說法；全部沒作答且
  errors＝0 的分支原本說 OOM「也長這樣」，實測只有 model not found 一種，已把 OOM 標成推測。
- ㊸ `tests/test_ci_toolchain.py` 新增兩條：所有 workflow 的 `promptfoo@` 釘版一致且等於
  fixture 的 `metadata.promptfooVersion`；eval-local 的 job 層 timeout 大於各步驟總和。
  `tests/fixtures/eval_local/README.md` 新增「升 promptfoo 版本時」的步驟；
  `docs/teacher-setup.md` 的首跑訂正指示補上 `.claude/skills/local-eval/SKILL.md` 第 3 步。
- 以上每項都在 scratchpad 沙箱做過突變回驗（改壞實作會紅；`curl --fail -s` 這種等價
  寫法維持綠）。
- 查過但沒有修、留給 owner：
  - **加分關驗不了 Lab 2 的 prompt 修復**（第 31 輪 Opus 反方論證；**owner 10-15 裁決：
    改定位，見下一節**）：07-16 PoC 用原版
    prompt 時 qwen2.5:1.5b 就已經掛在幻覺誘餌題，而 Lab 2 情境劇刪掉的那行只影響這一題，
    所以改壞前後、修回來都是同一種紅。lab2 README §3、`/lab2` 第 4 步、`mock_provider.js`
    註解卻把加分關介紹成「對真模型驗證」。要改定位還是改教法，屬教學設計，未動。
  - `quality.yml` 沒有 `permissions:` 區塊（base 既有、本 PR 沒動到那幾行）。
  - `summarize_eval.js` 對 stats 缺席、`stats.errors` 非數字、結果列為 null 的防禦檢查，
    拿掉後沒有測試會紅；promptfoo 不會寫出這些形狀，拿掉後也只會落到「未完成」，判定不補。
- 第 36、37 輪連續兩輪零 finding（收斂）。
- 本條目寫下時全套 pytest 104 綠 1 skip、`ruff check` 乾淨（本機 Python 3.12、node 26）。

### 2026-10-15（owner 裁決後：加分關改定位，並更正 3/3 對 1/3 的但書）

- **owner 裁決**：加分關看不出 Lab 2 情境劇那一行的作用 → 選「改定位」。
  `labs/lab2-golden-eval/README.md` 第 3 步、`.claude/skills/lab2/SKILL.md` 第 4 步、
  `mock_provider.js` 檔頭、`docs/teacher-setup.md`〈已知設計決策〉四處，不再說加分關能
  「對真模型驗證」這一行，改說它示範的是「同一份 golden 換模型重考」。
  `quality.yml` 缺 `permissions:` 那件另開 PR 補（repo 的 GITHUB_TOKEN 預設已是唯讀：
  `gh api repos/Bruce1986/vibe-to-prod-lab/actions/permissions/workflow` 回
  `default_workflow_permissions: read`）。
- 查證時翻出兩次 run 的 log（10-15 時仍可下載，GitHub 保存 90 天，之後就沒了，所以把
  原始輸出抄在這裡；JSON 的空白已壓縮，內容與欄位值逐字相同）：
  - 3/3：eval-live run `29418527554`（2026-07-15，commit `604242d`，gpt-4o-mini）。
    基本訂單 `{"status":"ok","items":[{"name":"珍珠奶茶","size":"L","sweetness":50,"ice":"少冰","toppings":[],"quantity":1}],"notes":""}`；
    誘餌 `{"status":"ok","items":[{"name":"珍珠奶茶","size":"L","sweetness":100,"ice":"去冰","toppings":["珍珠"],"quantity":1}],"notes":"加跳跳糖"}`；
    模糊輸入 `{"status":"need_clarification","question":"請問您想要點什麼飲品？"}`。
  - 1/3：eval-local PoC run `29495815414`（2026-07-16，`poc/ollama-eval` commit `e53c621`，
    qwen2.5:1.5b，渲染後的 prompt 含「配料只能使用菜單…」那一行）。
    基本訂單 `{"status":"ok","items":[{"name":"珍珠奶茶","size":"L","sweetness":50,"ice":"少冰","toppings":[],"quantity":1}],"notes":"(選填)"}`；
    誘餌 `{"status":"ok","items":[{"name":"珍珠奶茶","size":"L","sweetness":100,"ice":"去冰","toppings":["跳跳糖"],"quantity":1}],"notes":"(選填)"}`；
    模糊輸入 `{"status":"ok","items":[{"name":"珍珠奶茶","size":"M","sweetness":50,"ice":"少冰","toppings":[],"quantity":1}],"notes":"(選填)"}`。
- ㊹ **更正：3/3 與 1/3 用的是同一版斷言。** 兩個 commit 的 `tests.live.yaml` 都是舊式單行
  斷言（防禦性寫法是 08-16 `005a92a` 才進來的）。把上面六筆原始輸出用現行
  `tests.small.yaml` 的斷言（`tests/test_local_eval_asserts.py` 抽出的那三段）與
  `app/schemas/order.schema.json` 重判：gpt-4o-mini 三題全過；1.5B 只過基本訂單，誘餌題語意
  斷言與 schema 都不過（跳跳糖不在配料 enum 裡），模糊輸入語意斷言不過。也就是現行斷言
  同樣得到 3/3 與 1/3。lab2 README、`docs/02-llm-quality.md`、`slides/02` 講者備忘原本寫
  「兩次的斷言寫法不同、不是同一把尺」，前提不成立，已改成「同一版斷言、差距來自模型，
  但每邊只跑一次、只有 3 題」。`summarize_eval.js` 的但書講的是「之後每一次 run 與當年的
  3/3」，那兩者的斷言寫法確實不同，未改。本檔 ㉔、㉖ 的舊說法未逐字更正。
- 誘餌題 1.5B「上當」是實際輸出（toppings 裡有跳跳糖），不是格式或反問造成的 Fail。
  教材改定位時引用的就是這筆；刪掉那一行之後的結果仍沒有實測。

