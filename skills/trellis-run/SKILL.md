---
name: trellis-run
description: "Operator shell for `trellis run`, the unattended frontier loop runner — decides when a batch of tickets should be handed to the runner instead of worked interactively, what the tier and whitelist must already allow, where the run ledger lives, and what a stop line means for the board. Also the launch/monitor/takeover shell for an orchestrator-driven multi-agent run (the dispatch-roster skill's job ends once the roster is on disk). Load before running `trellis run`, when a run halts (cycle / fail threshold / push refused / always-stop / deferred delivery), before starting or taking over an orchestrator, or when asked what the runner will and will not do on its own. Requires .trellis/."
---

# trellis-run — loop runner operator shell

Thin shell: it routes to the repo-internal authority texts and carries
checklist-level judgment only. The gate model of record lives in the consuming
repo (`.trellis/domains/<board>/02-*.md` or wherever the delivery-tier document
sits) plus `.trellis/domains/DISCIPLINE.md` §4. The implementation is the
`oh-my-trellis` CLI (`trellis run`) and `task.py delivery-gate`. If this file and
those disagree, they win — correct this file.

**The runner's own stop conditions are mechanical, and so is the whitelist:
neither is negotiable from a prompt.** Nothing here lets a run push a protected
ref, merge a PR, tag, release, deploy, or run a production migration.

## When the loop is the right tool

- [ ] Several tickets in one board that are already specified (prd/design/
      implement written), each with a verification contract and a branch, and
      you are not needed between them → runner. One ticket, or one still being
      shaped → work it in-session. The runner does not think about scope.
- [ ] The board's flag protocol still applies inside the run: `task.py start`
      refuses on another writer's fresh flag, and that refusal counts as a
      ticket failure. A runner is not a bypass around a claimed board.
- [ ] Nothing unattended is worth doing unless its result is reviewable: the
      runner stops at a **ready-for-review PR**, and PR ≠ delivery — only a human
      merge closes a ticket, so a run that "finished" five tickets has delivered
      zero until they are merged and pulled.

## Before the first run in a repo

- [ ] Tier: `autonomy: supervised-delivery` in `.trellis/config.yaml`, otherwise
      the runner never pushes and every ticket stops as `delivery_deferred`
      (verified work left standing on its branch, unarchived — that is the
      correct outcome, not an error).
- [ ] Whitelist: `delivery.auto_push_refs` (block-list YAML, an empty or
      malformed list means no push). Ask the repo instead of guessing:
      `python ./.trellis/scripts/task.py delivery-gate <ref> --json`.
- [ ] Per ticket: `set-branch` + `set-base-branch` (no branch metadata = the
      ticket fails, the runner will not invent a ref) and a non-empty
      verification contract (`add-verify`) — without one nothing can be
      delivered unattended, because there is no evidence.
- [ ] Dry-run first: `trellis run --dry-run` prints the chosen ticket, its
      branch, the tier and the exact action plan, and writes nothing at all
      (not even a ledger file).

## Running

```bash
trellis run --until-empty --board <slug> --provider <claude|codex> \
            [--max-tickets N] [--max-failures N] [--timeout 20m] [--dry-run]
```

- [ ] Defaults are the board's: 5 ticket attempts per run, stop after 3
      consecutive failures on the same ticket.
- [ ] Each ticket gets its own worktree under `.trellis/.runtime/worktrees/` and
      exactly one headless worker. All ticket state changes (claim, verify,
      archive) land as commits **on the ticket branch**, so the repo you start
      from stays clean on the delivery path — with one deliberate exception: when
      a ticket hits the fail threshold, the runner marks `triage=ready-for-human`
      on the starting repo's copy, because that is the board a human reads next
      and the worktree carrying the ticket is already gone. Nothing else is
      written there. That is what keeps a bad run one `git revert` away.
- [ ] The commit is the worker's job. If its sandbox cannot write `.git`, the
      runner commits what the worker left, staging by explicit path and excluding
      task bookkeeping so the work commit stays revertable.
- [ ] Always-stop is verified twice against one authority: before the runner stages
      anything, and again against what the branch actually carries (`base..HEAD`),
      so a worker that committed `.env` or a board file itself is caught too. The
      rule list is `task.py check-commit` (Python), not a copy inside the runner —
      an agent committing by hand can ask the same verb and get the same answer.
- [ ] The worker runs under two clocks: the wall clock (`--timeout`) bounds a long
      ticket, and the idle clock (`channel.worker_guard.idle_timeout`, default
      5 minutes) gives up on a worker that emits no events at all. A busy worker is
      never judged idle. `max_live_workers` does not apply: the loop works one
      ticket at a time.
- [ ] The run ledger is `.trellis/.runtime/runs/run-<UTC>.jsonl` (gitignored).
      One line per action: ticket, worker, commit OID, verify command + exit,
      stop reason. It is a runtime trace, **never** a reconciliation source —
      truth stays git history > worklog > `## 进度`. Summarize it into the
      worklog's 验证 field at close-out like any other run.

## When a run stops

- [ ] `cycle` → nothing was grabbed. Correct the `blocked_by` graph
      (`task.py set-meta <dir> blocked_by …`), then re-run.
- [ ] `fail_threshold` → that ticket is now `triage=ready-for-human` on the
      board's copy: read its ledger lines, decide, and leave it to a human. Do
      not re-arm it by hand until the cause is gone.
- [ ] `push_refused` → the tier forbids it, the ref is protected, the whitelist
      never named it, or the gate's answer could not be read (unreadable and
      malformed config are refusals too — nobody is watching for a warning).
- [ ] `always_stop` → a board file or credential-shaped path landed in a commit on
      the ticket branch. The line stops before verify, push or PR. Read the ledger
      line for the path, decide by hand. Do not teach the worker to ignore it.
- [ ] `delivery_deferred` → work is verified and sitting unarchived on its
      branch. Either configure the tier/whitelist or deliver it by hand. The
      runner will not archive past a push it may not do.
- [ ] `no_grabbable_ticket` → everything ready is pending review or has a
      leftover worktree. Merge/close the first, look at the second. Do not
      delete the worktree until you have read the ledger line that mentions it.
- [ ] Always-stop still always-stops: destructive operations, credentials or
      real external side-effects, acting over a live flag, unanswerable
      ownership. A user's verbal stop outranks every tier.

## Orchestrator mode (multi-agent runs)

Single loop runner stays as above. When the roster is staffed and an
orchestrator drives the loop, the contract of record is the consuming repo's
`docs/agents/orchestrator-contract.md` (Laber carries it). This section is the
operational checklist, not the spec.

### Boundary with `dispatch-roster` — no overlap, no gap

- [ ] `dispatch-roster` owns “派给谁” and ends when the roster is **on disk**:
      probe → four decisions → summary → write cards / ticket `meta.worker` /
      `meta.model` / `meta.effort` / `config.yaml` `worker_default` +
      `orchestrator:` section. It asks“开跑吗？”(default no) and stops there.
- [ ] `trellis-run` owns “怎么跑” from that line onward: start the
      orchestrator, monitor the round, run the takeover protocol. This skill
      never rewrites the roster. Dispatch-roster never starts the runtime.
      If the `orchestrator:` config section is missing, the handoff back is
      to dispatch-roster (or the user), never improvisation.

### Standard opening — starting an orchestrator

- [ ] Read `.trellis/config.yaml` `orchestrator:` → card name (`agent`), model
      override, `max_parallel` (absent = 1). No section → stop. The roster was
      never written.
- [ ] Static layer first: `python ./.trellis/scripts/task.py validate <task>`
      per candidate ticket — missing cards, `provider: acp` without a
      registered `acp_target` (and no `acp_command` override), and bad
      `worker_default`/`orchestrator.agent` references are all hard errors.
      A ticket that fails validation is not dispatchable.
- [ ] Handshake probe before spawn: the card's provider/`acp_target` gets the
      same light probe dispatch-roster uses (`initialize` + `session/new`
      against the registry row). Needs pre-login or not installed → report
      and stop. Never fall back to a different agent.
- [ ] Spawn per the card: `trellis channel create <name>` then
      `trellis channel spawn <name> --agent <orchestrator.agent>` (add
      `--model <orchestrator.model>` when configured), with the contract doc
      passed via `--file` — or the supervising session claims the
      orchestrator role inline. Session-level claim is the exclusivity.
      Concurrent orchestrators are out of scope for v1 (`max_parallel: 1`
      anyway).
- [ ] First prompt points at the contract doc + current frontier snapshot.
      The orchestrator runs its own read-chain (编排接手 section). You do not
      pre-digest the board for it.

### Monitoring and takeover

- [ ] Monitoring = reading what landed on disk, not inventing a push channel:
      tail `.trellis/.runtime/runs/run-*.jsonl` (`attempt_started` /
      `attempt_finished` / `ticket_result`) and each `trellis run --ticket`
      child's last stdout line (the `TicketResult` JSON). Exit code alone is
      not the verdict — `delivery_deferred` exits 0.
- [ ] Orchestrator died or the session changed → run the takeover chain:
      this round's run ledger → the roster (cards + ticket meta + config) →
      `task.py frontier --json` → in-flight worktree verification. For a
      ticket with `attempt_started` and no `attempt_finished`, verify
      liveness (worktree residue, `run-<slug>-*` channel still emitting,
      child process alive). Dead → redispatch the same ticket, record it as a
      failed attempt that does **not** count toward strikes. Alive → wait
      for its close-out.
- [ ] Scan existing state before waiting: `channel messages --raw` and the
      ledger are the read path for what already happened. `channel wait`
      only sees future events.
- [ ] Close-out is the orchestrator's three on-disk writes, in order: summary
      report to the user → board worklog close-out section (its own
      `<platform>-<machine>-<writer>.md` file only — no flag line, no
      `## 进度` edits) → ledger closing row. If those three are not on disk,
      the round is not over — treat it as an interrupted one and take over.
