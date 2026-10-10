---
name: trellis-run
description: "Operator shell for `trellis run`, the unattended frontier loop runner — decides when a batch of tickets should be handed to the runner instead of worked interactively, what the tier and whitelist must already allow, where the run ledger lives, and what a stop line means for the board. Load before running `trellis run`, when a run halts (cycle / fail threshold / push refused / always-stop / deferred delivery), or when asked what the runner will and will not do on its own. Requires .trellis/."
---

# trellis-run — loop runner operator shell

Thin shell: it routes to the repo-internal authority texts and carries
checklist-level judgment only. The gate model of record lives in the consuming
repo (`.trellis/domains/<board>/02-*.md` or wherever the delivery-tier document
sits) plus `.trellis/domains/DISCIPLINE.md` §4; the implementation is the
`oh-my-trellis` CLI (`trellis run`) and `task.py delivery-gate`. If this file and
those disagree, they win — fix this file.

**The runner's own stop conditions are mechanical, and so is the whitelist:
neither is negotiable from a prompt.** Nothing here lets a run push a protected
ref, merge a PR, tag, release, deploy, or run a production migration.

## When the loop is the right tool

- [ ] Several tickets in one board that are already specified (prd/design/
      implement written), each with a verification contract and a branch, and
      you are not needed between them → runner. One ticket, or one still being
      shaped → work it in-session; the runner does not think about scope.
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
- [ ] Whitelist: `delivery.auto_push_refs` (block-list YAML; an empty or
      malformed list means no push). Ask the repo instead of guessing:
      `python ./.trellis/scripts/task.py delivery-gate <ref> --json`.
- [ ] Per ticket: `set-branch` + `set-base-branch` (no branch metadata = the
      ticket fails; the runner will not invent a ref) and a non-empty
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

- [ ] Defaults are the board's: 5 ticket attempts per run, halt after 3
      consecutive failures on the same ticket.
- [ ] Each ticket gets its own worktree under `.trellis/.runtime/worktrees/` and
      exactly one headless worker. All ticket state changes (claim, verify,
      archive) land as commits **on the ticket branch**, so the repo you launch
      from stays clean on the delivery path — with one deliberate exception: when
      a ticket hits the fail threshold, the runner marks `triage=ready-for-human`
      on the launching repo's copy, because that is the board a human reads next
      and the worktree carrying the ticket is already gone. Nothing else is
      written there. That is what keeps a bad run one `git revert` away.
- [ ] The commit is the worker's job; if its sandbox cannot write `.git`, the
      runner commits what the worker left, staging by explicit path and excluding
      task bookkeeping so the work commit stays revertable.
- [ ] Always-stop is checked twice against one authority: before the runner stages
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

- [ ] `cycle` → nothing was grabbed. Fix the `blocked_by` graph
      (`task.py set-meta <dir> blocked_by …`), then re-run.
- [ ] `fail_threshold` → that ticket is now `triage=ready-for-human` on the
      board's copy: read its ledger lines, decide, and leave it to a human. Do
      not re-arm it by hand until the cause is gone.
- [ ] `push_refused` → the tier forbids it, the ref is protected, the whitelist
      never named it, or the gate's answer could not be read (unreadable and
      malformed config are refusals too — nobody is watching for a warning).
- [ ] `always_stop` → a board file or credential-shaped path landed in a commit on
      the ticket branch. The line halts before verify, push or PR; read the ledger
      line for the path, decide by hand. Do not teach the worker to ignore it.
- [ ] `delivery_deferred` → work is verified and sitting unarchived on its
      branch. Either configure the tier/whitelist or deliver it by hand; the
      runner will not archive past a push it may not do.
- [ ] `no_grabbable_ticket` → everything ready is pending review or has a
      leftover worktree. Merge/close the first, look at the second; do not
      delete the worktree until you have read the ledger line that mentions it.
- [ ] Always-stop still always-stops: destructive operations, credentials or
      real external side-effects, acting over a live flag, unanswerable
      ownership. A user's verbal stop outranks every tier.
