---
marp: true
theme: default
paginate: true
headingDivider: 2
footer: '從 Vibe Coding 到 Production Architecture ｜ 下午場・Bruce'
style: |
  section { font-size: 26px; }
  section code { font-size: 0.85em; }
  section table { font-size: 0.78em; }
  section pre { font-size: 0.72em; }
---

# 單元二｜LLM／AI 系統品質驗證

**Golden Dataset ・ Prompt Regression ・ Hallucination Detection ・ Evaluation Pipeline**

從 Vibe Coding 到 Production Architecture — 下午場｜Bruce

<!-- 14:18 開講，本段 30 分、17 頁，節奏要抓緊。這段是全課重頭戲：把「AI 輸出不可預測」從焦慮變成工程問題。 -->

## LLM 品質問題長什麼樣（以珍奶 bot 為例）

| 類型 | 珍奶 bot 的版本 | 真實世界的版本 |
|---|---|---|
| **幻覺** | 配料出現「跳跳糖」 | 引用不存在的論文／API |
| **格式違約** | 甜度回「半糖」而非 `50` | JSON 缺欄位、多說廢話 |
| **瞎猜** | 「來點好喝的」→硬編訂單 | 資訊不足不反問、自信亂答 |
| **行為漂移** | 改 prompt 後六題錯三題 | 換模型版本後輸出悄悄變了 |

共同點：**「輸入 X 必得 Y」的傳統斷言框不住它們**

<!-- 2 分。用 boba 例子讓四個抽象詞落地。右欄帶一句就好，別展開。 -->

## 為什麼傳統測試不夠

- **非確定性**：同輸入兩次輸出可能不同（temperature、模型更新）
- **對錯是程度**不是布林：0.87 分的答案算過嗎？門檻誰定？
- **改動影響是全域的**：prompt 改一句話，六個場景三個變壞——
  你改的地方和壞掉的地方**不在同一行**
- 所以需要：**成批金標準 ＋ 自動判分 ＋ 進 CI** ＝ **eval**

一句話：**不可預測沒關係，量測它。**

<!-- 2 分。金句是最後一行，等一拍再翻頁。 -->

## 真實案例①：AI reviewer 把「現役模型」判成幻覺

講師自己的 code review 流水線遇過（去識別化轉述）：

- AI reviewer 連續三輪把程式裡**現役的 model ID** 判定為「幻覺、
  不存在」，並建議「降版」到一個**已經退役**的舊模型
- 原因：reviewer 自己的訓練資料比現實舊——**它的世界停在過去**
- 若當時照單全收，等於讓 AI 把正確的 code「修」成壞的

教訓：**評審者也是 LLM，它的判斷同樣需要被驗證**
（「訓練資料時效」類主張——新模型名、新 API——最容易被 AI 誤判）

<!-- 2 分。第一手故事，比教科書有說服力。講完丟問題：「那誰來審 reviewer？」→ 答案就是這個單元：用資料（golden set）當裁判。 -->

## Golden Dataset：你的 AI 考古題庫

一筆 golden case ＝ **輸入 ＋ 金標準該滿足的斷言**

樣本三來源：

1. **真實流量代表題**——最常見的訂單長相
2. **邊界與地雷**——衝突輸入、幻覺誘餌、模糊輸入
3. **事故回歸**——每次線上出包收一題，**永不再犯**

跟 code 一樣**進版控、走 review**：改 golden set ＝ 改規格

<!-- 2 分。「事故回歸」是最容易被忽略但最值錢的來源——單元三收尾會回扣這點形成閉環。 -->

## 真實案例②：365 個鄉鎮、69 個坑

講師在某 AI 產品 QA 期間實建的 golden set（去識別化）：

- 題庫：**全台 365 個鄉鎮市區**（政府開放資料，內政部 NLSC 官方清單）
- 測法：**裸名**輸入——「我想在**永安**買房」（不給縣市、不給區／鄉／鎮字尾）
- 全量掃描結果：**69 筆（19%）辨識錯誤**，且能分類歸因：

| 失敗模式 | 筆數 | 例子 |
|---|---|---|
| 配錯縣市 | 32 | 高雄「永安」→新北永和；苗栗「西湖」→臺北內湖 |
| 鄉鎮丟失 | 10 | 臺中「太平」→只剩臺中市 |
| 完全抓不到 | 27 | 「關西」「北港」→什麼都沒有 |

known-failing 清單做成 **monitor**（紅著追蹤何時修好），與迴歸 gate 分離

<!-- 2 分。第一手案例：地名歧義是台灣特色資料題——「永安」多個縣市都有、「關西」還會被聯想成日本。三個重點：(1) golden set 的題庫可以直接來自政府開放資料；(2) 失敗要分類，修復才能歸因；(3) 已知會紅的 monitor 和守迴歸的 gate 要分開（單元三伏筆）。時間緊就與上一頁併講。 -->

## Golden case 長相（本 repo 實檔）

```yaml
# labs/lab2-golden-eval/tests.yaml
- description: 幻覺配料（跳跳糖）不得出現在訂單 toppings
  vars:
    input: 一杯大杯珍珠奶茶全糖去冰，加跳跳糖
  assert:
    - type: javascript
      value: "!JSON.parse(output).items[0].toppings.includes('跳跳糖')"

- description: 模糊輸入必須反問，不能瞎猜
  vars:
    input: 來點好喝的
  assert:
    - type: javascript
      value: JSON.parse(output).status === 'need_clarification'
```

宣告式、可讀、可 review——**測資即文件**

<!-- 2 分。指著第一筆講「幻覺誘餌」的設計：故意在輸入裡放菜單外的東西，看模型會不會上當。 -->

## 判分三層：從便宜到昂貴

| 層 | 方法 | 成本 | 例 |
|---|---|---|---|
| 1 | **exact／規則**（含 JSON Schema） | 免費、快、穩 | `sweetness === 50`、過契約 |
| 2 | 語意相似（embedding、ROUGE…） | 便宜 | 摘要、改寫類任務 |
| 3 | **LLM-as-judge** | 貴、judge 也會錯 | 「有禮貌且未瞎猜」 |

原則：**能用第 1 層就不用第 3 層**
本課 lab 全用第 1 層 → 所以能零 API key、完全 deterministic

<!-- 1.5 分。三層是採購順序不是優劣排名：任務性質決定下限，成本紀律決定上限。 -->

## 真實資料點：AI 初判的嚴重度，過半撐不過查核

講師的多模型 review 流水線實測（去識別化統計）：

- AI reviewer 初判為「**高嚴重度**」的 findings，
  經事實查核後**超過一半**被降級或駁回
- 反過來，漏報不靠「調高單一模型的自信」解決，
  靠**加獨立視角**：不同模型抓到彼此的盲點

對 eval 的啟示：

- LLM-as-judge 的分數要**抽樣人工複核**（校準）
- 覆蓋面靠**多視角**，不靠單體自信

<!-- 2 分。這是我自己流水線的統計，數字保守講「過半」。它同時支撐兩個實務建議：judge 要校準、視角要多元。 -->

## Prompt Regression：prompt 也是 code

`app/prompts/order_prompt.txt` 裡有這麼一行：

```text
配料只能使用菜單配料：珍珠、波霸、椰果、仙草、布丁；
顧客點了菜單以外的配料就忽略，並在 notes 說明。
```

- 看起來囉嗦？**每一句約束都是某次翻車的疤痕**
- 改 prompt ＝ 改行為 ＝ 需要回歸測試：
  改 → 跑 golden set → 看 diff → 紅了就別上
- Vibe coding 常見事故：AI 幫你「精簡」prompt，順手刪掉約束——
  **Lab 2 會親手重演這場事故**

<!-- 2 分。「疤痕」這個比喻要講：prompt 的約束行和 golden 的事故題是同一件事的兩面。 -->

## 安全網收網的樣子（Lab 2 預告）

```
刪掉約束行 → push
   └─▶ CI: golden-eval ❌  6 題掛 5 題
         ├─ 甜度變字串（型別錯）      ├─ 冰塊枚舉外
         ├─ 數量變中文字              ├─ 跳跳糖上壘（幻覺）
         └─ 模糊輸入被瞎猜            ✅ 穩定 case 仍過
   └─▶ deploy-gate：沒跑（gate 擋下）
加回約束行 → push → 全綠 → gate 放行
```

**你改的是 prompt 的一行字，接住你的是六筆 golden**

<!-- 1.5 分。這頁是流程劇透，讓 lab 時每個人知道自己在哪一步。強調 deploy-gate 沒跑＝系統性保護，不靠人記得。 -->

## Evaluation Pipeline：把 eval 接進 CI（本 repo 實檔）

```yaml
# .github/workflows/quality.yml
golden-eval:
  needs: lint-test
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with: { node-version: 22 }
    - working-directory: labs/lab2-golden-eval
      run: npx -y promptfoo@0.121.19 eval -c promptfooconfig.yaml
```

- 工具：**promptfoo**（宣告式、離線斷言齊全、exit code 直接紅綠）
- 版本 **pin 死**——eval 工具跟 prompt 一樣要版控
- mock provider 回放預錄 fixtures → 課堂零 key；真模型見加分關

<!-- 2 分。指 pin 版本那行：工具本身也會變，eval 環境要可重現。 -->

## Hallucination Detection：方法選單

| 方法 | 原理一句話 | 成本／離線 |
|---|---|---|
| LLM-as-judge | 另一個 LLM 逐條裁決「有沒有依據」 | 貴；需 API 或本地模型 |
| **NLI 小模型** | 幾百 MB 分類模型判「是否被來源支持」 | **免費、CPU、可離線** |
| Citation 查核 | 引文真的在來源裡？真的支持該句？ | 幾乎免費（字串比對） |
| Self-consistency | 同題取樣 k 次，幻覺會彼此矛盾 | 生成成本 ×k |

沒有銀彈——**組合拳**：規則擋格式、NLI 顧事實、judge 管語氣

<!-- 1.5 分。表格快速過，重點是最後一行的分工觀。下一頁看真的。 -->

## Demo：把幻覺「標」出來（跟著看）

```bash
pip install lettucedetect        # MIT、17M–210M 參數、CPU 即時
```

- **LettuceDetect**：token 級把幻覺片段**螢光筆標紅**（有中文模型）
  - context：菜單與訂單事實 ｜ answer：AI 的回覆 → 紅的就是無依據
- **HHEM-2.1-Open**（Vectara、110M、Apache-2.0）：
  同一組 (context, answer) 打 **0–1 整體分**——與 span 標記互相印證
- 兩個都是**預先下載後可離線**的 CPU 小模型——放進 CI 也不心疼

<!-- 3 分（含 demo 切換）。講師機現場跑：一段有幻覺的珍奶回覆 → LettuceDetect 標紅「跳跳糖買一送一」→ HHEM 給低分。收尾一句：這就是把「感覺怪怪的」變成「0.23 分」。 -->

## 兩個讓人清醒的數據

- 2026 年的量測研究：商用 LLM 的 **citation 幻覺率 11%–57%**——
  「有附來源」≠「來源真的這樣說」
- 長文回答中，**5–9 成**的引用未被來源完整支持

所以：

- 引用查核（20 行 Python 的模糊比對）CP 值極高
- Self-consistency：同題取樣 5 次讓學生**先肉眼找矛盾**，
  再用 NLI 自動算一致性——SelfCheckGPT 的精神

<!-- 1.5 分。數據來源在深讀講義（arXiv 連結）。讓大家記住區間就好：「一到五成」。 -->

## LLM-as-judge 的三個誠實提醒＋一則訃聞

1. **Judge 也會錯**——它自己就是 LLM（想想案例①），判準要抽樣複核
2. **成本**——每筆檢查都是推論，golden set 大了要算錢
3. **可重現性**——judge 回應要 cache／預錄，否則 CI 紅綠會抖

一則訃聞：**OpenAI Evals 平台 2026-11-30 關閉**，官方教學教大家搬家
→ eval 工具選型要看**存續風險**；你的 golden set 要**工具中立**
（本 repo 同一批 golden 同時餵 promptfoo 與 pytest——雙軌就是保險）

<!-- 2 分。訃聞梗點到為止。工具中立是實務忠告：資產是 golden data，不是工具設定檔。 -->

## 帶回團隊的最小起步法（三步、一個下午）

1. **收 10 題**：5 題最常見輸入＋3 題邊界＋2 題歷史事故
2. **規則判分**：先全用第 1 層（schema＋關鍵欄位斷言），不碰 judge
3. **進 CI**：pin 版本、紅了擋 merge——從此 prompt 改動有安全網

之後再長大：題庫每週補、事故必收錄、需要語氣類判準才上 judge

**先有網，再求密。**

<!-- 1.5 分。給「明天回公司能做什麼」的答案。金句收尾。 -->

## Lab 2（20 分鐘）

打開 `labs/lab2-golden-eval/README.md`，或輸入 **`/lab2`**

1. 看綠色基準線（Actions → `golden-eval`）
2. **情境劇**：刪掉 prompt 約束行 → push → 看安全網收網（讀紅報告）
3. 修復回綠（`git revert` 或手動）
4. 加一筆**你自己的** golden case（fixtures＋tests.yaml 同步）
5. 加分關 **`/live-eval`**：GitHub Models 免 key 打真 LLM——
   看真模型過不過同一套契約

<!-- 14:48–15:08 實作＋提問，15:08–15:16 休息。巡場重點：改了 prompt 沒 push 的人（CI 不會動）、tests.yaml 的 input 沒和 fixtures key 一字不差的人。 -->
