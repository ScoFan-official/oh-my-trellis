---
name: agent-hygiene
description: "Cleanup-ticket acceptance contract: a task declared cleanup-only (hygiene / 大扫除 / cleanup-only) may only delete, reorder, rename, or equivalently refactor — scope prefix and the 800-line split-plan rule are mechanically enforced by the hygiene-sweep skill's scope_check.py. Consulted by the spec axis when reviewing any cleanup ticket."
---

# Cleanup-ticket acceptance contract (hygiene)

This contract defines the judgeable acceptance criteria for a "cleanup
ticket". It applies to any task whose `prd.md` declares cleanup-only intent
(contains `hygiene` / `大扫除` / `cleanup-only`). The spec axis rules on this
file; the standards axis may invoke the `scope_check.py` bundled with the
`hygiene-sweep` skill for evidence.

## 1. Diff shape

- Only four change kinds are allowed: delete, reorder, rename, equivalent
  refactor. Equivalent refactor means inputs, outputs, side effects and
  error behavior are identical.
- No new feature surface: new public functions, new commands, new API
  routes, new config keys, and new dependencies are all violations.
- No drive-by fixes: issues outside the findings list go into task notes or
  a new ticket — never into the diff.
- Tests must not regress: tests may be restructured with the refactor, but
  their asserted external behavior coverage must not shrink.

## 2. Scope gate

- The task must declare scope prefixes in `prd.md` (multiple allowed). Paths
  outside the scope must not appear in the diff.
- Mechanical check (run from the consuming repo root; `<skill-dir>` is where
  the `hygiene-sweep` skill was installed):

  ```bash
  python <skill-dir>/scripts/scope_check.py --scope <prefix>
  ```

- A changed file outside the scope prefix = FAIL. "It was convenient" is not
  a pass reason.

## 3. Line-count threshold

- When a file inside the scope exceeds the threshold (default 800 lines;
  `--max-lines` adjusts), the task must first deliver a split plan — no code
  edits to that file.
- A diff that touches an over-threshold file = FAIL, unless `implement.md`
  contains a split-plan section for that file.
- The threshold is a heuristic, not truth: a file already split along clear
  seams may be exempted, and the exemption reason must be written into
  `prd.md`.

## 4. Minimum verification set

- A cleanup ticket's `run-verify` contract includes at minimum: the
  project's existing test command plus the `scope_check.py` scope check.
- A pure-deletion ticket with no runnable tests: verification = a
  `scope_check.py` PASS plus the check axis confirming the diff contains
  only deletions.
