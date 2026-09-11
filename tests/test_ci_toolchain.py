"""CI 的工具鏈前提：node 不在，就不是「全綠」而是「什麼都沒測」。

`tests/test_eval_summary.py` 與 `tests/test_local_eval_asserts.py` 這兩份，
每一條都要真的叫 node 跑「線上那份」JavaScript（tests.small.yaml 的斷言、
summarize_eval.js 的判讀）。兩份都用 `skipif(node 不在)` 保護，本機沒裝 node
的人才跑得動 pytest——代價是**沒有 node 時它們整批靜默跳過、pytest 仍 exit 0**。
本機實測：`env -i PATH=<空目錄> pytest tests/test_eval_summary.py
tests/test_local_eval_asserts.py` → 全部 skipped、離開碼 0。

CI 上那正是最糟的失效：守門一條都沒跑，儀表板卻是綠的。所以在 CI 上把
「沒有 node」變成紅燈；本機維持可跳過。

刻意不在任何地方寫死「共幾條」：這個數字每次增修 parametrize 就會變，
寫死等於留一句遲早過期的宣稱（本檔第一版就寫了 35，當下實際是 38）。
"""

import os
import re
import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
QUALITY_WORKFLOW = REPO_ROOT / ".github" / "workflows" / "quality.yml"
IN_CI = os.environ.get("CI", "").lower() in {"1", "true", "yes"}


def test_lint_test_job_installs_node():
    """跑 pytest 的那個 job 必須自己裝 node，不能賭 runner 映像剛好有。

    這條才是真正擋得住回歸的那道：下面 `which("node")` 只看執行當下的 PATH，
    有人把 setup-node 從 quality.yml 拿掉、而 runner 剛好預裝 node 時，它照樣
    綠——於是「兩份 node 測試會不會跑」又變回沒有人保證的事。
    """
    workflow = QUALITY_WORKFLOW.read_text(encoding="utf-8")
    lint_test = workflow.split("  lint-test:", 1)
    assert len(lint_test) == 2, "找不到 lint-test job——這條測試已對不上 quality.yml"
    # 只看到下一個 job 為止，免得誤採 golden-eval 的 setup-node
    body = re.split(r"\n  \w[\w-]*:\n", lint_test[1])[0]
    assert "actions/setup-node" in body, (
        "lint-test 沒有 actions/setup-node：tests/test_eval_summary.py 與 "
        "tests/test_local_eval_asserts.py 會被整批靜默跳過，pytest 仍會全綠"
    )
    versions = set(re.findall(r"node-version:\s*\"?(\d+)\"?", workflow))
    assert len(versions) == 1, f"各軌的 node 版本應該一致，目前有 {sorted(versions)}"


@pytest.mark.skipif(not IN_CI, reason="本機允許沒有 node（那兩份會整批跳過）；CI 上不允許")
def test_node_is_available_in_ci():
    assert shutil.which("node"), (
        "CI 上找不到 node：tests/test_eval_summary.py 與 "
        "tests/test_local_eval_asserts.py 會被整批靜默跳過，pytest 仍會全綠。"
        "請確認 workflow 裡有 actions/setup-node。"
    )
