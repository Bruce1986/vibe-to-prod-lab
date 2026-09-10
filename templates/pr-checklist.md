# PR 品質 Checklist（AI 時代版）

課程「從 Vibe Coding 到 Production Architecture」下午場的帶回禮：
貼進你的 PR template，或直接給 AI 當自我檢查清單。

> 這是 `templates/coding-review-principles.md` 的可勾選版，**不是逐項一對一**。
> 14 項的組成：8 項出自 Review 八條（第 5 條拆成「幻覺 API」與「更嚴標準」兩項；
> 第 7 條「對事不對人」是 review 態度，沒有可勾選的對應項）、4 項出自撰寫十條第 1、
> 4、9 條（第 4 條在作者與 reviewer 兩區各一項；reviewer 區那一項與 Review 第 5 條的
> 「邊界條件、錯誤處理」重疊，這裡歸在撰寫十條）、2 項是本課程特有（LLM 輸出契約、
> golden set 回歸）。兩份會各自漂移而 CI 不會察覺，改動任一份時請一併確認另一份。
> 上面刻意不寫成相對連結——本檔設計上就是要整段貼進你的 PR template（例如
> `.github/pull_request_template.md`），一搬位置相對路徑就斷。

## 提交前（作者——不論人或 AI）

- [ ] CI 全綠（lint、format、test、型別檢查）——機器能抓的不要留給人
- [ ] 新增／修改的行為有對應測試，本機跑過全綠
- [ ] LLM 輸出有契約（JSON Schema 或等價物）保護
- [ ] prompt 有改動的話，golden set 跑過且通過
- [ ] 錯誤處理涵蓋：空值、逾時、重試、部分失敗（AI 最常漏這些）
- [ ] 沒有幻覺 API：新用到的函式／參數／套件確認真的存在
- [ ] diff 只含本次意圖；一個 PR 一件事、盡量 400 行以內
- [ ] commit 訊息講清楚「為什麼」，不是「做了什麼」的流水帳

## Review 時（reviewer）

- [ ] 先看行為再看風格；風格問題讓 linter 去吵
- [ ] 看不懂的段落＝需要重寫或補說明（「看起來很聰明」的 AI 碼尤其要小心）
- [ ] 邊界條件與錯誤路徑有測到，不只 happy path
- [ ] AI 生成的部分用更嚴標準：作者沒有「親手寫過」的記憶，你是第一個真正讀它的人
- [ ] 每條意見標優先級：blocker／suggestion／nit，nit 不擋 merge
- [ ] 兩個收尾問題：這段壞掉時我們怎麼知道？下一個改它的人需要知道什麼？
