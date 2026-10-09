---
name: agent-issue-tracker
description: "Issue tracker contract for mattpocock skills: specs, tickets, triage roles and wayfinder maps all live in .trellis/tasks/. Consulted before publishing anything an engineering skill produces."
---

# Issue tracker: Trellis tasks

This repo's issue tracker **is** the Trellis task system. Specs, tickets, triage roles and wayfinding maps live under `.trellis/tasks/` as Trellis task directories. Raw inbound requests wait in `.scratch/inbox/` until triage promotes them.

Manage tasks with `python ./.trellis/scripts/task.py` — it accepts a bare task name or a full path (`.trellis/tasks/<MM-DD-slug>/`).

## Nouns → where things live

| Tracker noun | Physical form |
| --- | --- |
| spec / feature | a Trellis task dir; requirements in `prd.md`, implementation decisions in `design.md`, test plan in `implement.md` |
| ticket | a **child task** (`task.py create --parent`); "what to build" + acceptance criteria in its `prd.md` |
| blocking edge | formal `task.json` `blocked_by` refs — `task.py set-meta <child-dir> blocked_by "<dir1> <dir2>"`; mirror them human-readable in a `## Blocked by` section of the child `prd.md` (`task.py frontier` reads the field, not the prose) |
| triage label | `task.py set-meta <dir> triage <role>` — never the `status` field (that enum is Trellis's: planning/in_progress/completed) |
| wayfinder map | `map.md` inside the parent task dir |
| decision ticket | a child task dir containing `question.md` (`Type:`/`Status:`/`Blocked by:` lines) and later `answer.md` |
| raw inbound item | `.scratch/inbox/<NN>-<slug>.md` with `Status:`/`Category:` lines |

## Verbs → what "the issue tracker" means here

- **"publish the spec"**: `python ./.trellis/scripts/task.py create "<title>" --slug <slug> --description "<one-liner>" --no-start`, then split the spec body across the task dir — Problem / Solution / User Stories / Out of Scope / Further Notes → `prd.md`; Implementation Decisions → `design.md`; Testing Decisions → `implement.md`. Keep the upstream rule: no file paths or code snippets, except decision-encoding prototype snippets.
- **"publish the tickets"**: one child task per ticket — `task.py create "<title>" --slug <slug> --parent <parent-dir> --no-start`, then wire dependencies with `task.py set-meta <child-dir> blocked_by "<dep1> <dep2>"` (`set-meta` is canonical and writes the formal field; `--meta blocked_by=…` on `create` still writes the legacy location and is read for compatibility). Write What-to-build + acceptance checklist into the child's `prd.md`, including a `## Blocked by` section (task dirs, or "None — can start immediately"). Then `task.py set-meta <child> triage ready-for-agent` (tickets are agent-grabbable by construction; skip triage for them).
- **"fetch the relevant ticket"**: read the task dir — `prd.md` first, then `design.md` / `implement.md` if present.
- **"apply triage label X"**: `task.py set-meta <dir> triage <role>`; on `.scratch/inbox/` files keep the `Status:` line convention instead.
- **"close work"**: `task.py archive <dir>` — moves the dir to `.trellis/tasks/archive/<YYYY-MM>/`, preserving all files. References by task slug keep working after the move.
- **frontier** (tickets whose blockers are done): `python ./.trellis/scripts/task.py frontier [--board <slug>] [--json]` — ready = every `blocked_by` ref completed or archived; blocked tickets list what they wait on; a cycle exits non-zero; a ref matching no task counts as unmet, never as ready.
- **starting implementation on a ticket**: `task.py start <dir>`. `start` refuses while `implement.jsonl` is still the empty seed on sub-agent platforms — curate context with `task.py add-context <dir> implement <file> "<why>"` first, or pass `--allow-empty-context` when intentionally PRD-only.

## Triage intake

- New inbound items (bug reports, external requests) start as `.scratch/inbox/<NN>-<slug>.md` with `Status:` (triage role) and `Category:` (`bug`/`enhancement`) lines — the original local-markdown convention.
- `needs-info`, `wontfix`, `ready-for-human` outcomes stay in the inbox.
- `ready-for-agent` **promotes**: `task.py create` a real task carrying the agent brief as its `prd.md`, `set-meta <dir> triage ready-for-agent`, then mark the inbox file `Status: promoted → <task-dir>`.

## Wayfinding operations

The map and its decision tickets are Trellis tasks:

- **Map**: `.trellis/tasks/<MM-DD-slug>/map.md` — Destination / Notes / Decisions so far / Not yet specified / Out of scope. Mark it `task.py set-meta <dir> wayfinder map`.
- **Child ticket**: `task.py create "<question>" --parent <map-dir> --no-start --meta ticket_type=<research|prototype|grilling|task>`; its `question.md` holds the question body plus `Type:` / `Status:` / `Blocked by:` lines.
- **Blocking**: a `Blocked by: <task-dir>, …` line in `question.md` plus `set-meta <dir> blocked_by` (the formal field). A ticket is unblocked when every dir it lists is completed or archived.
- **Frontier**: `task.py frontier` lists the ready children; also check `question.md` has no `Status: claimed`/`resolved` before grabbing (frontier reads task data, not the question file).
- **Claim**: write `Status: claimed` in `question.md` before any work.
- **Resolve**: write `answer.md` (the decision plus any facts later tickets need), set `Status: resolved`, append a one-line pointer (`[<question>](<child-dir>)`: gist) to the parent's `map.md` Decisions-so-far, then `task.py archive <child>`. Archive preserves files; reference children by slug.

## Why `.scratch/` still exists

Only as the triage **inbox** and true scratch space — drafts that haven't earned a task yet. Planned work never lives there; anything that does is a bug in the process, not a convention.
