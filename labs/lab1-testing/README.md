# Lab 1｜AI 時代的測試策略（約 15 分鐘）

目標：親手體驗四層防線——**單元、整合、契約、回歸**——在 AI 專案裡各自接住什麼。

## 0. 環境準備（開場時完成）

Windows（PowerShell）：

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS／Linux：

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

檢查起點：`python -m pytest -q` → 應該全綠。

## 1. 讀懂現有的四類測試（3 分鐘）

- `tests/test_service.py`：**單元**（直接測 `validate_business_rules`）＋
  **整合**（FakeLLMClient 走完 `parse_order` 全流程）
- `tests/test_contract.py`：**契約**——schema 要同時「不誤殺 good」與「抓得住 sloppy」
- `tests/test_golden.py`：**回歸**（golden dataset，lab2 的主角，先知道它在這）

問自己：幻覺配料「跳跳糖」是哪一層擋下的？為什麼不是單元測試？

## 2. 完成兩個學員測試（7 分鐘）

打開 `tests/test_lab1_student.py`，完成兩個 TODO。
可以請 AI 幫忙（輸入 `/lab1`），但建議先自己想 Arrange → Act → Assert 三段。

驗收：`python -m pytest -q` 的通過數 **+2**。

## 3. 契約層的手感（3 分鐘）

```bash
python -c "
from app.llm_client import FakeLLMClient
from app.service import parse_order
parse_order('一杯大杯珍珠奶茶全糖去冰，加跳跳糖', FakeLLMClient(variant='sloppy'))
"
```

讀一下 `OrderContractError` 的錯誤訊息——契約錯誤要「說人話」，
這是可維護性的一部分。

## 4. 回歸的手感（2 分鐘）

把 `app/service.py` 的 `MAX_QUANTITY_PER_ITEM` 改成 `100` → `python -m pytest -q`
轉紅 → 改回 `10` → 回綠。

感受一件事：**測試不是考試，是你（和你的 AI）未來改 code 的安全網。**
