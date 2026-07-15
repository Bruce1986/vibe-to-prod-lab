# 深讀講義｜單元一：AI 時代的測試策略

> 投影片：`slides/01-testing-strategy.md`（課堂版）；本文是課後深讀版。

## 核心論點

AI 讓「寫 code」變便宜，同時讓「未驗證的 code」變多。品質的信任來源從
「我寫的我知道」轉移到「驗證過的才算數」——測試從「有空再補」變成
AI 協作的**前提設施**。

## 四層測試在 AI 專案的分工

1. **單元測試**：測純邏輯，毫秒級、可窮舉邊界。可測試性來自設計：
   依賴注入、面向介面（與上午 Clean Architecture 的 Dependency Rule 同源）。
   本 repo 範例：`tests/test_service.py` 直接餵 dict 測 `validate_business_rules`。
2. **整合測試**：測接縫。LLM 是外部依賴，藏在 `LLMClient` 介面後，
   測試注入 `FakeLLMClient` 回放預錄回應——快、免費、deterministic，
   還能強制回放壞輸出來測錯誤路徑。
3. **契約測試**：把 LLM 輸出當「不可信的外部輸入」。JSON Schema 是可執行的
   spec（呼應上午的 API Contract／Schema）。雙向驗證缺一不可：
   good 全過（不誤殺）、已知 sloppy 全擋（抓得住）。
   schema 管不到的跨欄位規則交給業務層——分層把關，錯誤訊息各自說人話。
4. **回歸測試**：AI 改 code 的安全網。每次 AI 重構、修 bug、「順手優化」，
   都該有網子接著；單元二把同一概念延伸到 prompt。

## 成本論證（課堂數據的出處）

「有無單元測試的 bug 修復成本相差 29 倍（保守估 2.5 倍）」與
「文件協作比會議省 9.4 倍」的完整推導：

- 你就是不寫測試才會沒時間：<https://brucejhang.com/tw/topics/brucelectures/why_you_should_write_unit_test.html>
- 為什麼你應該寫文件：<https://brucejhang.com/tw/topics/brucelectures/why_you_should_write_documents.html>

## 延伸閱讀

- 測試金字塔與測試配比、Code Review 文化：
  <https://brucejhang.com/tw/topics/knowledge/google-software-engineering-deep-dive-article.html>
- 可測試性與解耦（SOLID、DI）：
  <https://brucejhang.com/tw/topics/knowledge/code-decoupling-guide-article.html>
- 自動化測試全景（含 CI/CD 與 AI 在測試的角色）：
  <https://brucejhang.com/tw/topics/knowledge/android-automated-testing-deep-dive-article.html>
