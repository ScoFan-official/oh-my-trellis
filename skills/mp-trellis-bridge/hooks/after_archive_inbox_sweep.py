"""Trellis after_archive hook: sweep .scratch/inbox entries promoted to the archived task.

Reads TASK_JSON_PATH (set by Trellis lifecycle hooks). Finds inbox files whose
`Status: promoted -> <task>` marker points at the archived task and moves them
to `.scratch/inbox/done/` so the inbox only ever shows live intake.

Wire in .trellis/config.yaml:

    hooks:
      after_archive:
        - "python ./tools/mp-trellis-pack/hooks/after_archive_inbox_sweep.py"
"""

from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

PROMOTED_RE = re.compile(r"^\s*Status:\s*promoted\s*->\s*(\S+)\s*$", re.MULTILINE)


def task_names(task_json_path: Path) -> set[str]:
    """Names the archived task can be referenced by: dir name, id, name."""
    import json

    names = {task_json_path.parent.name}
    try:
        data = json.loads(task_json_path.read_text(encoding="utf-8"))
        for key in ("id", "name"):
            value = data.get(key)
            if isinstance(value, str) and value:
                names.add(value)
    except Exception:
        pass
    return names


def main() -> int:
    task_json_path = os.environ.get("TASK_JSON_PATH")
    if not task_json_path:
        return 0

    path = Path(task_json_path)
    if not path.exists():
        return 0

    repo_root = path.parent
    for _ in range(4):
        if (repo_root / ".trellis").is_dir():
            break
        repo_root = repo_root.parent
    else:
        return 0

    inbox = repo_root / ".scratch" / "inbox"
    if not inbox.is_dir():
        return 0

    targets = task_names(path)
    done = inbox / "done"
    moved = []
    for file in sorted(inbox.glob("*.md")):
        try:
            text = file.read_text(encoding="utf-8")
        except Exception:
            continue
        match = PROMOTED_RE.search(text)
        if not match or match.group(1) not in targets:
            continue
        done.mkdir(exist_ok=True)
        shutil.move(str(file), str(done / file.name))
        moved.append(file.name)

    if moved:
        print(f"inbox sweep: moved {', '.join(moved)} -> .scratch/inbox/done/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
