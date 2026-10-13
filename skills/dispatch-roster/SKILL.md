---
name: dispatch-roster
description: "Staffs the dispatch roster (派工表) for an unattended multi-agent run: probes every ACP target in the registry (grok-build / codex / claude) with a light initialize+session/new handshake and a credential check, asks the four roster decisions (orchestrator, role defaults for implement/check/research, per-ticket overrides, max_parallel), shows a summary for explicit confirmation, then writes the roster to agent-card frontmatter, ticket meta and .trellis/config.yaml. Load when the user says 无人值守 / 放手跑 / hands-off 跑 / unattended, when a planning skill lands tickets meant for agent execution (wayfinder map, grill-with-docs spec, to-tickets split, trellis-brainstorm close-out), or whenever asked who should run what. This skill ends when the roster is on disk — launching, monitoring and takeover belong to trellis-run. Requires .trellis/."
---

# dispatch-roster — 派工表装配

Thin pipeline: **probe → four decisions → summary → confirm → write → ask开跑**.
The roster contract of record is the multi-agent orchestration design (§3) plus
what `python ./.trellis/scripts/task.py validate <task>` enforces statically —
if this file and the validator disagree, the validator wins.

## Boundary with `trellis-run` — no overlap, no gap

- [ ] `dispatch-roster` owns “派给谁” and ends the moment the roster is **on
      disk**: card frontmatter (`provider: acp` / `acp_target` / `model` /
      `effort`), ticket `meta.worker` / `meta.model` / `meta.effort`, and
      `config.yaml` `worker_default:` + the `orchestrator:` section.
- [ ] `trellis-run` owns “怎么跑” from that line onward: spawning the
      orchestrator, monitoring the round, takeover. This skill never spawns an
      orchestrator or worker, never runs `trellis run`, and never edits a card
      body — frontmatter only.
- [ ] If the user answers yes at the final“开跑吗”question, the handoff is to
      the `trellis-run` skill's *Standard opening* section — not to anything
      improvised here.

## When to load

- [ ] Keywords anywhere: “无人值守”“放手跑”“hands-off 跑”/ unattended run
      → load this skill directly.
- [ ] Planning close-outs that produced agent-bound tickets: `wayfinder` map
      written, `grill-with-docs` spec converged, `to-tickets` split landed,
      `trellis-brainstorm` final summary approved → the closing question“要
      无人值守跑吗？”lands here on yes.
- [ ] Any request to (re)staff the roster: change orchestrator, swap a role's
      target, add a per-ticket override, change `max_parallel`.
- [ ] Not for interactive work: one ticket being worked in-session needs no
      roster. A roster for zero upcoming tickets is not roster material.

## Step 1 — Probe: light handshake, three states

Run the bundled probe against every registry target (grok-build / codex /
claude — the ids `task.py validate` accepts, the table mirrors the CLI's
bundled `acp-agents.json`):

```bash
python <this-skill-dir>/probe_roster.py            # all targets, human report
python <this-skill-dir>/probe_roster.py --json     # machine-readable
python <this-skill-dir>/probe_roster.py --target claude --prompt-check
```

For each target the probe spawns the registry row, sends `initialize` then
`session/new` on a throwaway cwd (<1s per agent once the package is in npx
cache), reads `authMethods` + `configOptions` (`category:"model"` = the live
model list — never quote a model from a static table), then a credential
probe settles the state:

- **可用 available** — handshake ok and cached credentials present (or the
  agent advertises no authMethods). Roster freely.
- **需预登录 needs pre-login** — handshake ok but the credential probe fails
  (typical: the `authMethods` are all terminal-type with no cached creds).
  Show the exact login command and flag the target red in the summary. It may
  still be rostered, but the run cannot start until a human logs in once.
  Login commands: grok-build → `grok login`; codex → `codex login`（或
  `codex login --with-api-key`）. Claude → `claude auth login --claudeai`
  （或 `--console`）.
- **未安装 not installed** — process did not spawn or never answered.
  Excluded from the decision options.
- `--prompt-check` escalation sends a trivial `session/prompt`. A `-32000
  Authentication required` confirms needs-login, a `stopReason` confirms
  available. Use it when the credential probe is ambiguous.

The real commands to start a target (Windows forms shown — on POSIX drop the `cmd /c`
wrapper and call `npx -y <pkg>` directly):

```
grok-build : grok agent --always-approve stdio
             # --always-approve is a `grok agent` PARENT option; it must
             # precede `stdio` or grok errors "unexpected argument"
codex      : cmd /c npx -y @agentclientprotocol/codex-acp
             # env: CODEX_PATH=<codex exe resolved from PATH>,
             #      INITIAL_AGENT_MODE=agent-full-access
claude     : cmd /c npx -y @agentclientprotocol/claude-agent-acp
```

Windows notes: `npx` is a `.cmd` — always via `cmd.exe /c`. Stdio is
newline-delimited JSON-RPC over UTF-8, one message per line, stderr is logs
only. If `probe_roster.py` cannot run, speak the same two requests by hand —
`initialize` `{protocolVersion:1, clientCapabilities:{fs:{readTextFile:false,
writeTextFile:false}, terminal:false, auth:{terminal:true}}}` then
`session/new` `{cwd:<tempdir>, mcpServers:[]}` — and classify by the same
rules. `--registry <path>` points the probe at the CLI's real
`acp-agents.json` when a fork adds rows.

## Step 2 — Ask the four decisions

Present the probe table first (state, models, current model, effort options,
login command where needed). Then ask — one batched block or one at a time,
matching this repo's question norms — always with a recommendation:

1. **Orchestrator 选哪家** — which target drives the `orchestrator` card, and
   its model. Recommend the strongest available target. A needs-login target
   is legal but flagged.
2. **三角色默认** — `implement` / `check` / `research` each get a target +
   model (+ optional `effort`). `check` may split into two axis cards,
   `check.standards` + `check.spec` (dotted names are the established
   pattern). When they exist they win over `check` for their axis. Different
   roles may use different targets.
3. **票级覆盖** — which tickets pin a worker: ticket dir → card name via
   `meta.worker` (+ optional `meta.model` / `meta.effort`). The value is a
   **card name**, not a target id. If no existing card carries the wanted
   target, create `<role>.<slug>.md` (e.g. `implement.grok`) — copy the role
   card's body verbatim, change only the frontmatter.
4. **并发** — `orchestrator.max_parallel`, default **1**. Backpressure beyond
   that is `channel.worker_guard`'s job.

Never ask which model — offer the probed `configOptions` list. Inventing a
model id fails at spawn time.

## Step 3 — Summary, then explicit confirmation

Render the full roster before writing anything. Wait for an explicit yes:

```
派工表（待确认）
  orchestrator   orchestrator  → claude  (model: opus)      ⚠ 需预登录: claude auth login --claudeai
  implement      implement     → codex   (model: gpt-5.6-sol, effort: high)
  check          check.standards→ grok-build (model: grok-4.7)
                 check.spec    → grok-build (model: grok-4.7)
  research       research      → codex   (model: gpt-5.5)
  worker_default → implement
  max_parallel   1
  票级覆盖       .trellis/tasks/10-12-foo → meta.worker=implement.grok
                 ✗ grok-build 未安装的行不会出现；⚠ 行标出需预登录目标
```

Mark every needs-login target with its login command. Silently dropping a
flagged target is how unattended runs die at spawn. No write before the
user's yes.

## Step 4 — Write the roster (after confirmation only)

Write in this order. Every shape is one `task.py validate` can confirm:

- [ ] **Role cards** (`.trellis/agents/<role>.md` frontmatter, bodies
      untouched): set `provider: acp`, `acp_target: <grok-build|codex|claude>`,
      `model: <model-id from the probe>`, `effort: <level>` — replacing the
      existing `provider:` value and the commented ACP block. Splitting
      `check`: copy `check.md` body into `check.standards.md` / `check.spec.md`,
      adjust only frontmatter `name`/`description`/ACP fields.
- [ ] **Orchestrator card**: same treatment for `acp_target`. Its model lives
      in config (`orchestrator.model`), its `effort` on the card.
- [ ] **Tickets**: `python ./.trellis/scripts/task.py set-meta <task-dir>
      worker <card>`; optionally `model`/`effort` the same way. Non-empty
      strings only.
- [ ] **`.trellis/config.yaml`**: in the "Dispatch roster" section, set
      `worker_default: <card>` and the `orchestrator:` block
      (`agent:` card name, `model:` id, `max_parallel:` positive int) —
      uncomment the shipped template or write the same shape. Keep the
      surrounding comments.
- [ ] **Confirm**: `python ./.trellis/scripts/task.py validate <task>` for
      every rostered ticket — expect zero roster problems. A problem means
      the write was wrong. Fix the write, never the validator's message.

Schema recap (what the validator rejects): missing card file. `provider: acp`
without `acp_target`. `acp_target` outside `grok-build|codex|claude` without
an `acp_command:` override. `model:`/`effort:` on a card whose unlisted
target resolves only via `acp_command` (they would be silently dropped —
pass them through `acp_args`). `[`-form `acp_args` that is not a JSON string
array. `worker_default` / `orchestrator.agent` naming a nonexistent card.
Non-integer `max_parallel`. Empty `meta.model`/`meta.effort`.

## Step 5 — 开跑吗 (default: no)

After the write and validation, end with exactly one question:

> 派工表已落盘。现在交给 orchestrator 开跑吗？（默认否 — 答“跑”才启动）

- Explicit yes (跑 / yes / 开跑) → load `trellis-run` and follow its
  *Standard opening* — never start the run from inside this skill.
- Anything else (silence included) → stop. Report what was written: cards
  touched, ticket meta set, config lines, validation result.

## Never

- Spawn an orchestrator/worker or run `trellis run` — that is `trellis-run`'s
  side of the line.
- Roster a `not_installed` target, or a needs-login target without flagging
  the login command.
- Write card bodies, ticket `prd.md`, or any file the schema doesn't name.
  Ticket meta changes go through `task.py set-meta`, never hand-edited
  `task.json`.
- `git commit` / `git push` / `git merge` — the supervising session owns
  commits.
