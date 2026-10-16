---
name: hygiene-sweep
description: "Read-only inventory audit inside a declared scope prefix: find dead code, duplicated logic and oversized files, write a durable findings list, never touch product code. Use when the user asks for 大扫除 / 清理 / dead code sweep / duplicate logic / hygiene audit on a module, or when a cleanup ticket needs a findings list before any edit. Approved deletions are executed in a separate cleanup ticket. The acceptance contract is .trellis/spec/agents/hygiene.md. Requires .trellis/ for the task-dir report path. Without a task it writes to .scratch/."
---

# hygiene-sweep — read-only inventory audit

Input = a scope prefix. Output = a findings list on disk. This skill never
edits product code.

## Scope discipline

- Get the scope prefix from `prd.md` or the user before scanning (multiple
  prefixes are allowed). If the scope is unclear, stop and ask. Do not default
  to the whole repo.
- Read only files under the scope prefix. Files outside the scope must not be
  opened and must not enter the findings list.
- Write the scope prefix into the findings list header so a later cleanup
  ticket inherits it unchanged.

## Procedure

1. Resolve the scope prefix and run the line-count scan:

   ```bash
   python <skill-dir>/scripts/scope_check.py --scope <prefix> --scan-oversize
   ```

   `<skill-dir>` is wherever this skill was installed (e.g.
   `.devin/skills/hygiene-sweep`, `.agents/skills/hygiene-sweep`).

2. Scan each in-scope file read-only and classify findings: dead code
   (unreferenced exports / unreachable branches / commented-out
   implementations), duplicated logic (the same-shaped logic in 2+ places),
   oversized files (from step 1), leftover probes and debug residue.
3. Record four fields per finding: location (`file:line`), type, evidence
   (who references it / who does not), and proposed handling (delete / merge /
   split) with a one-line reason.
4. Oversized files get a split-plan section only: the proposed seam, each
   part's responsibility, and the recommended order. Do not write code.
5. Write the list to `{TASK_DIR}/research/hygiene-sweep.md`. Without an active
   task write to `.scratch/`. In chat report only the conclusion and the file
   location.
6. Stop-line report: N findings total — M mechanically executable, K needing
   a human ruling.

## Judgment rules

- "Dead" requires evidence: a repo-wide search shows no references, or every
  referrer is itself dead. When unsure, mark `存疑` (doubtful) — never `删`.
- Duplicated logic must be same-shaped. Merely similar behavior is marked
  `相似` and not merged into the same case.
- The list is a list: it must not contain "already fixed in passing" entries.
  The urge to fix in passing goes to a "separate proposals" section at the
  end of the list.

## Follow-up

- After the user rules on the list, open a cleanup child ticket
  (`blocked_by` this ticket) and execute item by item under `simplify`'s
  behavior-preserving discipline.
- The cleanup ticket is accepted against `.trellis/spec/agents/hygiene.md`:
  the diff may only delete, reorder, rename, or equivalently refactor.
