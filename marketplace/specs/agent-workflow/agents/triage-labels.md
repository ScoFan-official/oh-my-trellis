---
name: agent-triage-labels
description: "Triage label vocabulary for mattpocock skills and where each role is stored: task meta.triage for Trellis tasks, Status: lines for .scratch/inbox files."
paths:
  - ".scratch/"
  - ".trellis/tasks/"
---

# Triage label vocabulary

The `/triage` skill moves inbound items through a small role machine. Label names are **roles in the triage workflow**, not Trellis task statuses — never write them to `task.json.status`.

## Roles

| Label | Meaning | Next action |
| --- | --- | --- |
| `needs-triage` | Raw item, not yet evaluated | Read, verify, assign a real role |
| `needs-info` | Can't decide yet — missing reproduction, context or answers | Ask the reporter; keep the item in the inbox |
| `ready-for-agent` | Verified, well-scoped; an agent brief exists | Promote to a Trellis task / hand to `/implement` |
| `ready-for-human` | Needs human judgment or privileged access | Assign to a person |
| `wontfix` | Out of scope per `.out-of-scope/` or repo direction | Record the rationale; close |

Classification is orthogonal: `Category: bug | enhancement`.

## Storage

- **On a Trellis task**: `python ./.trellis/scripts/task.py set-meta <dir> triage <role>` — inspectable via `task.py list --json` (`meta.triage`).
- **On an inbox file** (`.scratch/inbox/*.md`): a `Status:` line in the frontmatter-style header, e.g. `Status: needs-info`.

`/to-tickets` output skips triage: child tasks get `meta.triage=ready-for-agent` at creation.
