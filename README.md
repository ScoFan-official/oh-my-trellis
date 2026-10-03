# mp-trellis-pack

A reusable public template that fuses [mattpocock/skills](https://github.com/mattpocock/skills) with a [Trellis](https://github.com/mindfold-ai/Trellis)-managed repository — distributed through **two complementary channels**.

mattpocock's engineering skills (`/to-spec`, `/to-tickets`, `/triage`, `/wayfinder`, `/implement`) speak in terms of an abstract "issue tracker". This pack answers that abstraction with **the Trellis task system itself**: specs become `.trellis/tasks/` directories, tickets become child tasks with `blocked_by` metadata, triage roles become task `meta` keys, and wayfinder maps live inside parent tasks. Upstream skill files are never modified, so `npx skills update` stays safe.

## Install channel 1 — Trellis spec registry (contracts)

```bash
trellis init --registry gh:ScoFan-official/mp-trellis-pack/marketplace --template agent-workflow --append
```

Installs the contract specs into `.trellis/spec/`:

```
.trellis/spec/
├── agents/
│   ├── index.md
│   ├── issue-tracker.md      # THE contract — paths: .trellis/tasks/, .scratch/
│   ├── triage-labels.md      # five roles → meta.triage / Status: lines
│   └── domain.md             # GLOSSARY.md + docs/adr/ conventions
└── guides/
    └── mp-integration.md     # phase map, lane rules, skill precedence
```

`--append` adds missing files only — safe on existing spec trees. Contract files carry `paths:` frontmatter, so Trellis's dynamic spec loading injects them exactly when the agent touches task artifacts, the inbox, or domain docs.

## Install channel 2 — skills CLI (the bridge skill)

```bash
# mattpocock's skills (skip if already installed)
npx skills add mattpocock/skills --agent devin --copy

# the bridge: routing contract + first-run bootstrapper
npx skills add ScoFan-official/mp-trellis-pack --agent devin --copy
```

The `mp-trellis-bridge` skill carries the same contracts as fallback templates and bootstraps the whole thing on first load: verify `.trellis/`, install spec contracts (registry first, templates second), append an `## Agent skills` block to `AGENTS.md`, check the mp skill set is present. It's a no-op afterwards.

## Why two channels

- The **spec registry** is Trellis's native extension point — contracts live where Trellis expects specs and get path-scoped injection for free.
- The **skills CLI** is what Trellis doesn't ship (docs: "no automated installer for external skills") — it delivers the skill itself plus bootstrap logic, lockfile-tracked updates, and per-platform `--agent` targeting.

Either channel alone is sufficient; together they self-heal.

## Layout

```
marketplace/
├── index.json                          # registry index (type: "spec")
└── specs/agent-workflow/               # installed → .trellis/spec/
    ├── README.md  index.md
    ├── agents/                         # contracts (paths-scoped)
    └── guides/mp-integration.md
skills/mp-trellis-bridge/
    ├── SKILL.md                        # contract + bootstrap
    ├── templates/                      # same files as spec fallback
    └── hooks/after_archive_inbox_sweep.py
```

## Optional lifecycle hook

`skills/mp-trellis-bridge/hooks/after_archive_inbox_sweep.py` clears `.scratch/inbox/` files marked `Status: promoted → <task>` when that task is archived. Wire it in `.trellis/config.yaml` (adjust the path to your agent's skills dir):

```yaml
hooks:
  after_archive:
    - "python ./.devin/skills/mp-trellis-bridge/hooks/after_archive_inbox_sweep.py"
```

Or per-task in `task.json` under `hooks.after_archive`. Hooks receive `TASK_JSON_PATH` in the environment; failures warn without blocking.

## Updating

- Bridge skill: `npx skills update` (lockfile-tracked).
- Spec contracts: rerun the `trellis init --registry ... --append` command. Already-installed files are project-owned — review and merge changes intentionally, per Trellis's authoring model.

## Requirements

- A Trellis-managed repo (`.trellis/scripts/task.py` present)
- `npx skills` (Node.js) for channel 2
- mattpocock/skills for the skills this pack routes (the bridge alone does nothing)
