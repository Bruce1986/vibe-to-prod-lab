# Code Review Style Guide

> 此檔供 Gemini Code Assist 與其他 AI 審查工具讀取，作為本專案的審查標準。
> 規則由歷史 AI review 意見歸納而成，聚焦最常反覆出現的問題。

## 0. 分級與態度
- **high**：會崩潰、資安漏洞、資料遺失、破壞既有行為。
- **medium**：健壯性、正確性邊界、可維護性改善。
- 不為湊數挑芝麻；該肯定就具體肯定，完全沒問題就照 0.1 的固定句明確收尾（不要再混用「LGTM」等其他寫法，全專案統一一個收尾句）。
- 每條意見要有完整因果鏈（輸入 → 操作 → 具名例外/錯誤 → 後果）＋可套用的修正。

### 0.1 正向回饋與無回饋
- **問題不多／僅輕微時**：先具體肯定做得好的地方，再給建議——不要只挑毛病。
  - 點名值得鼓勵的良好實踐（結構清晰、錯誤處理完整、測試齊全、命名一致、資安防護到位等），用一句總評定調，例如：「Overall, this is an excellent contribution.」「整體而言，這是一次很棒的改進。」
  - 肯定要具體、對應到實際 diff，不是空泛客套；再接「a couple of minor suggestions」等小建議。
- **完全沒問題時**：明確回覆固定句 `I have no feedback to provide.`
  - 可視情況補上理由，例如：`I have no feedback to provide as the implementation is robust and well-tested.`
  - 沒有任何 review comment 可評時：`There are no review comments, and I have no feedback to provide.`
- 不為湊數硬找問題；該肯定就肯定，沒問題就照上述固定句明確收尾，不要含糊帶過。

## 1. 一致性與重複（DRY）
- 相同邏輯出現第二次就抽共用函式／常數，不複製貼上。
- 同一概念全專案用同一名稱；新增程式碼比照鄰近既有風格。
- 文件/設定中同一符號、欄位、標題層級在各處保持一致。

## 2. 不要硬編碼
- 路徑、URL、門檻值、魔術數字抽成具名常數或設定（config/env）。
- 重複出現的字串字面量改為常數。

## 3. 例外與錯誤處理
- 對每個 I/O、解析、外部呼叫點，盤點會拋的**具名例外**，並**有意識地**決定：在此攔截處理，或刻意往上拋到統一的邊界層處理（避免到處重複、破碎的 try/except）。
  - `json.loads` → `json.JSONDecodeError`（屬 `ValueError`）
  - `requests` 的 `resp.json()` 可能拋 `ValueError`（其他 client 如 `httpx`/`aiohttp` 的 decode 例外型別不同，依所用 library 列出對應例外）
  - `subprocess.run` 工具不存在 → `FileNotFoundError`
- 禁止裸 `except:` 或過寬 `except Exception` 吞掉所有錯。
- 容錯載入時**不可把壞檔覆寫成空值**（保留原檔待修）。

## 4. None / 空值
- `d.get("k", "")` 當值為 `null` 時仍回 `None`（因為 key 存在）。若只想處理 `None`，用明確判斷：
  `v = d.get("k"); v = "" if v is None else v`。
- 慎用 `d.get("k") or ""`：它簡潔，但會把合法的 falsy 值（`0`、`False`、空 list/dict）一併變成 `""`；**僅在這些值不該出現時**才用。
- 對可能為 `None` 的值做字串操作前先降級。

## 5. 型別防禦
- 外部 JSON/API 回傳先檢查型別再使用，別假設結構：`isinstance(x, (list, dict))`，或分別檢查 `list` / `dict`。
- 預期 list 卻可能拿到 dict（如 API 錯誤物件）→ 防禦處理。

## 6. 時間與資源
- 時間戳一律帶時區：`datetime.now(timezone.utc)`，不用 naive `datetime.now()`。
- 檔案／連線／鎖一律用 `with`（context manager），不裸開。

## 7. 資安
- SQL 一律參數化查詢，不字串拼接。
- `subprocess` 不用 `shell=True`；命令參數用 list 形式。
- 不硬編碼密鑰／token，從環境變數讀。

## 8. 供應鏈 / 依賴
- 依賴版本升級時，確認該版號**真實存在**於官方 registry。
- 可疑的大跳版或不存在的版本 → 視為潛在供應鏈攻擊／幻覺，擋下查證。

## 9. 測試
- 新增函式／分支邏輯要有對應單元測試，涵蓋正常 + 邊界 + 例外路徑。

## 10. 邊界與輸入
- 空輸入、空集合、越界、off-by-one、除以零先處理。

## 11. 文件與 Markdown
- 標題層級語義化且一致：依文件結構遞進使用 `##`、`###`、`####`，不要用粗體假標題（利於目錄生成）。
- LaTeX：數學符號用 `$...$` 包；用 `\langle\rangle` 而非 `\<\>`；避免多餘 `\\`。
- 長文件加目錄/內部連結；圖表排版、符號定義跨段一致。
