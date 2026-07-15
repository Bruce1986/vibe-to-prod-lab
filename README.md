# vibe-to-prod-lab

[![quality](https://github.com/Bruce1986/vibe-to-prod-lab/actions/workflows/quality.yml/badge.svg)](https://github.com/Bruce1986/vibe-to-prod-lab/actions/workflows/quality.yml)

臺大計中課程 **「從 Vibe Coding 到 Production Architecture」下午場
（Testing & Quality Engineering）** 的教學 repo（2026-08-18，講師：Bruce）。

示範應用是一個**珍奶點餐 bot**：把顧客的口語訂單轉成結構化 JSON。
所有 LLM 呼叫都用**預錄 fixtures 回放**——零 API key、完全 deterministic，
而 determinism 本身就是本課的教學重點之一。

投影片：<https://bruce1986.github.io/vibe-to-prod-lab/>

## 快速開始（3 步）

1. 按右上角 **Use this template → Create a new repository**，建立你自己的 repo
   （不要 fork；template 給你乾淨起點，commit 也算進你的貢獻圖）。
2. Clone 下來、用 VS Code 開啟 repo 根目錄
   （AI 助理用 **Claude Code** 或 **GitHub Copilot** 擇一）。
3. 在 AI 助理輸入 **`/course-help`**——它會告訴你下一步。

> 零設定就生效的原因：repo 根目錄的 `AGENTS.md` 是規範的唯一事實來源，
> Copilot 原生讀它、Claude Code 透過 `CLAUDE.md` 的 `@AGENTS.md` 讀它，
> 而 `.claude/skills/` 的自訂指令兩邊工具都認得。

## 三個 Lab

| Lab | 主題 | 時間 | 入口 |
|---|---|---|---|
| 1 | 單元／整合／契約／回歸測試 | 15 分 | [labs/lab1-testing](labs/lab1-testing/README.md) 或 `/lab1` |
| 2 | Golden Dataset 與 Prompt Regression | 20 分 | [labs/lab2-golden-eval](labs/lab2-golden-eval/README.md) 或 `/lab2` |
| 3 | CI/CD、Observability、Logging | 15 分 | [labs/lab3-production](labs/lab3-production/README.md) 或 `/lab3` |
| 加分關 | 免 API key 打真 LLM（GitHub Models） | 選配 | `/live-eval` |

## Repo 地圖

```
app/            珍奶點餐 bot（LLMClient 介面＋FakeLLM、業務邏輯、輸出契約 schema、prompt）
fixtures/       預錄 LLM 回應（good／sloppy 兩變體；sloppy 是刻意錯誤的教學樣本）
tests/          pytest：單元／整合／契約／golden ＋ Lab 1 學員練習區
labs/           三個 lab 的導引（各自有 README 與 AGENTS.md）
slides/         Marp 投影片（push 後由 CI 自動發佈 GitHub Pages）
docs/           深讀講義（課後看）＋講師設定
templates/      帶回你團隊用的範本：AGENTS.sample.md、PR checklist、CI 範本
.claude/skills/ /course-help /lab1 /lab2 /lab3 /live-eval（兩種 AI 工具通用）
.github/workflows/  quality（品質管線）、eval-live（加分關）、slides（投影片）
```

## 環境需求

- Python 3.10+（教室機 3.9 亦可）、Git、VS Code＋AI 擴充（Claude 或 Copilot）
- 免 Docker、免 API key；Node 只有「想在本機跑 promptfoo」時才需要
  （不裝也行，push 上 GitHub 讓 CI 跑）

```bash
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1 ／ macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m pytest -q   # 全綠 = 起點正確
```

## FAQ

**Q：為什麼不用真的 LLM？**
課堂主軌用預錄回放，所以零 key、零費用、結果可重現——這正是「把 LLM
隔離在介面後面」的測試設計。想打真模型：`/live-eval` 用 GitHub Models
免 key 跑（在 GitHub Actions 上，有 rate limit）。

**Q：mock 怎麼知道我的 prompt 變好變壞？**
教學模擬器：`mock_provider.js` 與 `FakeLLMClient` 以 prompt 是否包含
關鍵約束句「配料只能使用菜單」決定回放 good 或 sloppy 變體（機制完全
透明，見 [labs/lab2-golden-eval/README.md](labs/lab2-golden-eval/README.md)）。
真實世界請對真模型跑 eval。

**Q：課後想把這套搬回團隊？**
從 [templates/](templates/) 開始：AGENTS.sample.md（改名 AGENTS.md 放你的
repo root）、pr-checklist.md、workflows/quality.sample.yml。

## 授權

MIT（含教材文字；歡迎拿去教你的團隊）。
