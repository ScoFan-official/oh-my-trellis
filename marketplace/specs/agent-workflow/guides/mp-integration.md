# mattpocock × Trellis integration guide

Trellis owns the pipeline; mattpocock skills supply the techniques inside each phase. The `agents/` specs in this template make the fusion concrete: when a mattpocock skill says "the issue tracker", it means `.trellis/tasks/`.

## Phase map

```
/grill-with-docs          align the requirement; lands GLOSSARY/ADR entries   │ think
  ├ open question  → /handoff → /prototype → /handoff back                    │
  └ can't answer   → /to-questionnaire                                        │
/to-spec      → Trellis task + prd/design/implement.md                        │ record
/to-tickets   → child tasks + blocked_by field (tracer-bullet slices)         │
task.py validate → task.py frontier → task.py start                           │
/implement    → /tdd inside; trellis-before-dev reads specs                   │
  stuck on a bug → /diagnosing-bugs; looping → trellis-break-loop             │ do
trellis-check → mp /code-review (complementary, both run)                     │
trellis-update-spec + /domain-modeling + /retro                               │ distill
task.py archive                                                               │
```

Unattended lane — available once the repo sets `autonomy: supervised-delivery`
and a non-empty `delivery.auto_push_refs`. `trellis run` takes the frontier head
per ticket, gives it a worktree and one headless worker, runs the ticket's own
verify contract, then asks `task.py delivery-gate <branch>` before touching a
remote:

```
trellis run --until-empty --board <slug> --provider <claude|codex>
  → worktree → worker → run-verify → delivery-gate → push branch → ready PR → archive
  stop lines: cycle · 3 consecutive failures (ticket → triage=ready-for-human)
              · protected or unlisted ref → refused, the whole line halts
              · tier refuses push → deferred: verified work stays on its branch
```

Two properties to keep in mind: the loop never writes to the repo it is launched
from (ticket state changes are commits on the ticket branch, so a bad run is one
`git revert` away), and **PR ≠ 交付** — a board row closes only when a human
merges. `.trellis/.runtime/runs/*.jsonl` is the run ledger: one line per action
for the worklog's 验证 field, never a reconciliation source. The `trellis-run`
skill carries the operator checklist.

Frontend tasks get a second lane, owned by the `impeccable` skill and bound by
`agents/frontend-craft.md` (delivered via the agents index; its design-review
gate is mechanical at `archive`):

```
no spec/product.md → init bootstrap (product truth → .trellis/spec/)          │ think
prd done → /impeccable shape  → task design.md = surface brief                │ record
/implement → craft loop; read craft-floor.md before ANY UI edit               │ do
trellis-check → /impeccable audit + critique                                  │
verification: implement.md needs ## Design review — archive refuses           │
finish → /impeccable polish → archive                                         │ distill
```

On-ramps: external requests → `.scratch/inbox/` → `/triage` → `ready-for-agent` promotes to a task. Fog-level work → `/wayfinder` (map = parent task, decision tickets = child tasks).

## Lane rules

- **Active Trellis task** → Trellis owns the phase; mp skills run inside steps (grilling inside `trellis-brainstorm`, `tdd` during implementation, `code-review` after `trellis-check`).
- **No active task, quick work** → standalone mp lane: grill → implement → code-review, no task needed. Promote to a task when it outgrows one session.
- **Promotion boundary** → inbox items become tasks only at `ready-for-agent`.

## Name collisions

- Inside a task: prefer the Trellis variants in `.agents/skills/` (`feature-development`, `tdd-workflow`, `verification-loop`) — they read `prd.md` and acceptance items.
- Outside tasks: the mattpocock versions.
- `trellis-check` vs mp `code-review` are complementary, never alternatives.

## Context hygiene

- grill → spec → tickets stays inside one context window.
- One ticket per implementation session; tickets are self-contained.
- Wayfinder resolves at most one decision ticket per session.

## Devin note

`/implement` and `/implement-spec` ship `agents/openai.yaml` (Codex sub-agent format) that Devin does not execute — run tickets sequentially in the main session or delegate with `run_subagent` manually.

## Updating

- mattpocock skills: `npx skills update` (per `skills-lock.json`). Skills are `--copy` installed — do not patch them in place.
- This template: `trellis init --registry <source> --template agent-workflow --append` refreshes missing files; already-installed files are project-owned and reviewed manually.
- To change the contract itself (tracker mapping, labels, domain layout), edit `agents/*.md` here and treat it like any spec change.
