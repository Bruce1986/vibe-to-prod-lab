"""CI 的工具鏈前提：node 不在，就不是「全綠」而是「什麼都沒測」。

`tests/test_eval_summary.py` 與 `tests/test_local_eval_asserts.py` 合計 35 條
測試都要真的叫 node 跑「線上那份」JavaScript（tests.small.yaml 的斷言、
summarize_eval.js 的判讀）。兩份都用 `skipif(node 不在)` 保護，本機沒裝 node
的人才跑得動 pytest——代價是**沒有 node 時它們會靜默跳過、pytest 仍 exit 0**。
本機實測：`env -i PATH=<空目錄> pytest tests/test_eval_summary.py
tests/test_local_eval_asserts.py` → `35 skipped`、離開碼 0。

CI 上那正是最糟的失效：守門一條都沒跑，儀表板卻是綠的。所以在 CI 上把
「沒有 node」變成紅燈；本機維持可跳過。
"""

import os
import shutil

import pytest

IN_CI = os.environ.get("CI", "").lower() in {"1", "true", "yes"}


@pytest.mark.skipif(not IN_CI, reason="本機允許沒有 node（那 35 條會跳過）；CI 上不允許")
def test_node_is_available_in_ci():
    assert shutil.which("node"), (
        "CI 上找不到 node：tests/test_eval_summary.py 與 "
        "tests/test_local_eval_asserts.py 的 35 條守門會被靜默跳過，"
        "pytest 仍會全綠。請確認 workflow 裡有 actions/setup-node。"
    )
