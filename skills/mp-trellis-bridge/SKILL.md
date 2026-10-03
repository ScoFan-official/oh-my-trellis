---
name: mp-trellis-bridge
description: "Bridge contract between mattpocock engineering skills and a Trellis-managed repo. Load before running /to-spec, /to-tickets, /triage, /wayfinder, /implement, or whenever a mattpocock skill mentions 'the issue tracker', tickets, labels, or triage roles. Requires .trellis/."
---

# mattpocock × Trellis bridge

In a Trellis-managed repo, **"the issue tracker" IS the Trellis task system**. The contract lives at `.trellis/spec/agents/issue-tracker.md` (spec → task dir + `prd.md`/`design.md`/`implement.md`; ticket → child task + `blocked_by` meta; triage role → `task.json` meta key; wayfinder map → parent task + `map.md`). Read it before publishing anything a mattpocock skill produces. `.scratch/` is only the triage inbox and scratch space — planned work never lives there.

## First-run setup (bootstrap)

If `.trellis/spec/agents/issue-tracker.md` is missing, run setup once before using the engineering skills:

1. **Verify Trellis**: `.trellis/scripts/task.py` must exist. If not, stop and tell the user — this bridge only works in Trellis-managed repos.
2. **Install the spec contracts** — two ways, pick the first that works:
   - Preferred: `trellis init --registry gh:ScoFan-official/mp-trellis-pack/marketplace --template agent-workflow --append` (installs `agents/` + `guides/` specs, including `paths:` frontmatter for dynamic spec loading). `--append` adds missing files only — safe on existing `.trellis/spec/` trees.
   - Fallback: copy `templates/issue-tracker.md`, `templates/triage-labels.md`, `templates/domain.md`, `templates/index.md` from this skill's directory into `.trellis/spec/agents/` (create the directory; skip files that already exist and report each skip).
3. **Register the block**: append an `## Agent skills` section to `AGENTS.md` — strictly outside any `TRELLIS:START`/`TRELLIS:END` markers. Skip if the section already exists; create `AGENTS.md` with just that section if the file is missing. Use the block template below.
4. **Check the skill set**: look for mattpocock skills (`grill-with-docs`, `to-spec`) in this agent's skills directory. If absent, tell the user to run `npx skills add mattpocock/skills --agent <their-platform> --copy` — the bridge is a contract layer, not the skills.
5. **Optional hooks**: automation examples live in this skill's own `hooks/` directory. They wire into `.trellis/config.yaml`'s `hooks:` section or per-task `task.json` hooks. Do not edit `config.yaml` unprompted.
6. **Full asset catalog**: the pack repo also vendors mattpocock + Everything-Claude-Code assets (1,700+: skills/sub-agents/commands/MCPs). Install any subset for 22 platforms via `python <pack>/scripts/install.py --platform <platform> --target <repo>`; see the pack README.

Report what was created/skipped, then continue with whatever invoked this skill.

## AGENTS.md block template

```markdown
## Agent skills

### Issue tracker

The tracker IS the Trellis task system: specs/tickets land in `.trellis/tasks/` (spec → task dir + `prd.md`; ticket → child task + `blocked_by` meta). `.scratch/inbox/` holds raw inbound items awaiting triage. See `.trellis/spec/agents/issue-tracker.md`.

### Triage labels

Five-role vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) as task `meta.triage` values. See `.trellis/spec/agents/triage-labels.md`.

### Domain docs

Single-context: `GLOSSARY.md` + `docs/adr/` at repo root, created lazily by `/domain-modeling`. See `.trellis/spec/agents/domain.md`.
```

## Lane rules

- **Active Trellis task** → the Trellis pipeline owns the phase; mp skills run inside steps (grilling inside `trellis-brainstorm`, `tdd` inside implementation, mp `code-review` after `trellis-check`). Do not let an mp skill create new tasks mid-flight without telling the user.
- **No active task, quick work** → standalone mp lane: grill → implement → code-review, no Trellis task needed. If the work grows past one session, promote it: `/to-spec` → `/to-tickets`, which land in `.trellis/tasks/`.
- **Promotion boundary**: `.scratch/inbox/` items become real tasks only when triage lands `ready-for-agent`.

## Skill precedence on name collisions

- Inside a task: prefer `.agents/skills/` Trellis variants (`feature-development`, `tdd-workflow`, `verification-loop`) — they read `prd.md` and acceptance items.
- Outside tasks: the mattpocock versions.
- `trellis-check` and mp `code-review` are complementary: check = spec/lint/tests; review = two-axis (Standards + Spec) diff analysis.
