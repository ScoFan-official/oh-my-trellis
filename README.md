# mp-trellis-pack

A distributable bridge that fuses [mattpocock/skills](https://github.com/mattpocock/skills) with a [Trellis](https://github.com/mindfold-ai/Trellis)-managed repository — installable in one command via the `skills` CLI.

## What it does

mattpocock's engineering skills (`/to-spec`, `/to-tickets`, `/triage`, `/wayfinder`, `/implement`) speak in terms of an abstract "issue tracker". This pack answers that abstraction with **the Trellis task system itself**: specs become `.trellis/tasks/` directories, tickets become child tasks with `blocked_by` metadata, triage roles become task `meta` keys, and wayfinder maps live inside parent tasks. Upstream skill files are never modified, so `npx skills update` stays safe.

It also ships the lane rules that keep the two systems from fighting (Trellis owns the pipeline inside an active task; mp skills own the quick lane outside one).

## Install

```bash
# 1. mattpocock's skills (skip if already installed)
npx skills add mattpocock/skills --agent devin --copy

# 2. this bridge
npx skills add <your-account>/mp-trellis-pack --agent devin --copy
```

Then mention a tracker concept or invoke `/mp-trellis-bridge` once — the skill's bootstrap section seeds `docs/agents/*.md`, registers an `## Agent skills` block in `AGENTS.md`, and verifies prerequisites. It's a no-op afterwards.

## Update

```bash
npx skills update
```

## Contents

```
skills/mp-trellis-bridge/
├── SKILL.md            # routing contract + first-run bootstrap
├── templates/          # seeded into docs/agents/ on first run
│   ├── issue-tracker.md
│   ├── triage-labels.md
│   └── domain.md
└── hooks/
    └── after_archive_inbox_sweep.py   # optional task lifecycle hook
```

## Optional lifecycle hook

`hooks/after_archive_inbox_sweep.py` clears `.scratch/inbox/` files marked `Status: promoted → <task>` when that task is archived. Once the skill is installed, wire it in `.trellis/config.yaml` (adjust the path to your agent's skills dir):

```yaml
hooks:
  after_archive:
    - "python ./.devin/skills/mp-trellis-bridge/hooks/after_archive_inbox_sweep.py"
```

Or per-task in `task.json` under `hooks.after_archive`. Hooks receive `TASK_JSON_PATH` in the environment; failures warn without blocking.

## Requirements

- A Trellis-managed repo (`.trellis/scripts/task.py` present)
- `npx skills` (Node.js)
- mattpocock/skills installed for the skills this pack routes (the bridge alone does nothing)
