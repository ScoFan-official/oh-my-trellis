---
name: rules-audit
description: "Reconcile always-loaded rule files against reality: enumerate every instruction in AGENTS.md / CLAUDE.md and friends, find evidence in code and environment, mark evidence-free rules for deletion, annotate kept rules with a one-line reason. Use when the user asks to audit / clean up AGENTS.md, CLAUDE.md, rules files, or 规则大扫除, or suspects rule files only grow and have drifted from the code. Judgment criteria follow writing-for-agents: relevance / sediment / no-op / cache."
---

# rules-audit — always-loaded rules reconciliation

Object = the rule files that enter context every round. Criterion = whether
each rule still has evidence in the code or the environment. The default
output is an audit report; give the user a ruling point before deleting.

## Audit objects

- Default targets: repo-root `AGENTS.md`, `CLAUDE.md`. The user may name
  other always-loaded files (e.g. `.cursor/rules/`, `.devin/rules/`).
- Board files under `.trellis/domains/**` (BOUNDARY / NN-* / worklog /
  review) are append-only by discipline and out of scope for this skill.

## Procedure

1. Enumerate rules: split each target file into individually judgeable
   instructions and number them.
2. Collect evidence per rule — one of three kinds:
   - Command exists: the script / command the rule cites is present and runs.
   - Path exists: the file / directory the rule cites is still in place.
   - Convention still honored: sampled code search shows the convention has
     live traces (naming, structure, call shapes).
3. Rule per line: `keep` (evidence found and still relevant) / `prune` (no
   evidence — a stale rule for code that no longer exists) / `annotate`
   (keep, but append one line stating why it exists). Reasons may cite the
   writing-for-agents criteria: relevance (does it still serve this file's
   purpose), sediment (an add-only sediment layer), no-op (it states default
   behavior), cache (it restates environment-queryable facts).
4. Write the report to `{TASK_DIR}/research/rules-audit.md` (or `.scratch/`
   without a task): each entry = source line number + ruling + evidence or
   the missing evidence.
5. Apply by autonomy tier: `gated` delivers the report and waits for a
   ruling; `hands-off` / `supervised-delivery` edit directly — delete
   `prune` lines, append "（保留原因：…）" to `annotate` lines — and attach a
   diff summary to the report. If no autonomy tier is configured, default
   to `gated`.
6. After editing, run `python ./.trellis/scripts/voice_lint.py --changed`
   when that script exists in the consuming repo.

## Discipline

- Every ruling needs evidence or a stated lack of evidence — never batch-
  delete on impression.
- An `annotate` addition is one sentence stating why the rule is needed; do
  not restate the rule text.
- Mark doubtful entries `存疑` with the missing evidence spelled out, and
  hand them to the user; do not fold them into `prune`.
- Deletions and annotations land in the same commit; the report cites that
  commit.
