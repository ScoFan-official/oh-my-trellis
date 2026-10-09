---
name: trellis-domains
description: "Operator shell for the Trellis domain layer (.trellis/domains/). Load when routing a task to a domain (归口), taking or releasing a board's construction flag (插旗/拔旗), hitting another writer's flag (撞旗) or judging a stale one (腐旗), running the session-takeover read chain + five-line restatement (接手), writing worklog entries or closing out work (收工), or reconciling board state (对账). Requires .trellis/."
---

# trellis-domains — domain layer operator shell

Thin shell: this file routes you to the repo-internal authority documents and
carries checklist-level indexes only. **The protocol text of record lives in
the consuming repo — read it at run time; do not quote or paraphrase it into
other artifacts.** If this file and the authority texts ever disagree, the
repo files win — fix this file.

Authority map (paths are relative to the consuming repo root):

| Topic | Authority |
|---|---|
| 归口 routing · flag protocol · takeover · autonomy modes · always-stop | `.trellis/domains/DISCIPLINE.md` (§1 归口路由 / §2 施工旗协议 / §3 接手协议 / §4 自主档位 + 永远拦人 / §5 文件纪律 / §6 违规速查) |
| worklog file rules · entry fields · 收工一单制 · 对账清单 | `.trellis/domains/WORKLOG-PROTOCOL.md` |
| board index · registration rules · skeleton template | `.trellis/domains/REGISTRY.md` · `.trellis/domains/_scaffold/` |
| per-board state | `.trellis/domains/<slug>/README.md` (first line = flag slot; `## 进度` table) · `BOUNDARY.md` · `NN-*` docs · `worklog/` · `review/` |

If `DISCIPLINE.md` / `WORKLOG-PROTOCOL.md` are absent, the domain layer is not
installed in this repo — run `trellis update` (or tell the user to) before
operating on `.trellis/domains/`; do not improvise protocol.

Ground rule (everything else defers to it): truth is committed git history —
an uncommitted flag, progress tick or log entry does not exist
(`WORKLOG-PROTOCOL.md` §0).

## When this fires

| Situation | Checklist below |
|---|---|
| Creating a task / about to write product code | 归口 |
| Starting writes on a domain board | 旗 |
| Board's first line shows another writer's flag | 撞旗/腐旗 |
| New session taking over a task | 接手 |
| Writing worklog / closing out a work segment | worklog & 收工 |
| Auditing or repairing board state | 对账 |

## 归口 — routing a task to a domain (DISCIPLINE.md §1)

- [ ] Scan `.trellis/domains/REGISTRY.md` before product-code work; when a
      registry line is ambiguous, read the candidate boards'
      `README.md` / `BOUNDARY.md` before deciding.
- [ ] Owning board exists → record `meta.domain = "<slug>"` in `task.json` and
      a `Domain: .trellis/domains/<slug>/` line atop `prd.md`.
- [ ] No board fits → create one first: copy `_scaffold/` to
      `.trellis/domains/<slug>/` and add its REGISTRY line — **same commit** —
      then create the task.
- [ ] Truly domain-less (whitelist in §1) → leave `meta.domain` empty; a
      `Domain: none（<reason>）` line atop `prd.md` is still mandatory.
- [ ] Cannot answer "who owns this" → STOP and ask the user — an always-stop
      rule; every autonomy tier blocks.

## 旗 — taking / releasing a board flag (DISCIPLINE.md §2)

- [ ] Read the flag slot: the first line of
      `.trellis/domains/<slug>/README.md` (`head -1`).
- [ ] No flag (or a stale flag resolved per the next checklist) → plant yours
      in the format defined by §2 (also spelled out in the
      `_scaffold/README.md` comment); **committing is what makes it real** —
      only then start writing.
- [ ] Flag scope = write rights to `domains/<slug>/` plus the product code of
      tasks hung on it. Reads are always free — no flag needed.
- [ ] Multi-board task → one flag per affected board; domain-less work plants
      none.
- [ ] 收工 releases the flag by deleting the flag line inside the close-out
      commit (see worklog & 收工).

## 撞旗 / 腐旗 — another writer's flag (DISCIPLINE.md §2)

- [ ] Valid flag (not yours, still fresh) → do not touch the board or its
      tasks' product code; report who holds it, since when, and in which
      context; then wait — an always-stop rule in every tier.
- [ ] Stale judgement = the three anchors in §2 (flag timestamp · last
      `git log` activity on the board dir · that writer's newest worklog
      entry). Self-check the facts; do not ask others for them.
- [ ] Verdict stale → you may 代拔: remove their flag and plant yours in one
      commit, and log the evidence chain plus the original flag line verbatim
      in **your own** worklog file — never edit theirs.
- [ ] Same-time collision (flags planted blind to each other) → first commit
      wins; the loser withdraws the flag, logs the cession and the winner's
      flag line, then moves on or waits.

## 接手 — session takeover (DISCIPLINE.md §3)

- [ ] Pick the tier: same-session continuation → skip; domain task → full
      chain; `Domain: none` task → light chain (task artifacts + journal
      summary); cross-writer / cross-machine → full chain + the stale-flag
      check above.
- [ ] Full chain order: `REGISTRY.md` → board `README.md` (flag slot +
      `## 进度`) → `BOUNDARY.md` → `NN-*` (`状态:已定版` first) → `worklog/`,
      anchoring on `[~]`/`[!]`/`🔄`/`⛔` markers.
- [ ] Output the five-line restatement (defined by §3): task dir + status ·
      domain ownership · flag status + disposition · latest worklog entry ID
      + ancestor check on its cited commit · next action. Any line missing =
      takeover incomplete — do not start work.
- [ ] `trellis mem` is optional background — never a substitute for the
      chain, never a fact source.

## worklog & 收工 (WORKLOG-PROTOCOL.md §1–§4)

- [ ] Write only your own file `worklog/<platform>-<machine>-<writer>.md`;
      newest entry on top; cross-file references by entry ID only.
- [ ] Open an entry when work starts; roll-update that same entry for the
      task; required fields per §2.
- [ ] Domain work → worklog; domain-less work → journal only (split per §3).
- [ ] 收工一单制 (§4): entry update + `## 进度` tick + flag-line removal +
      code land in **one commit** — bookkeeping written first, flag removed
      last.
- [ ] Progress states `[ ]/[~]/[x]/[!]`; rows are written when `NN-*` entries
      land — an empty skeleton table is normal, not debt.

## 对账 — reconciliation (WORKLOG-PROTOCOL.md §5; precedence also in DISCIPLINE.md §3)

- [ ] Fixed precedence: **git history > worklog entries > README `## 进度`**;
      journal never participates.
- [ ] Anchor in-flight/blocked work by grepping the board for the markers —
      never infer idle/busy from the top of a file.
- [ ] Verify cited commits with `git merge-base --is-ancestor <hash> HEAD`;
      rerun an entry's 验证 commands (guards against phantom foundations).
- [ ] Discrepancy → log it and the adopted correction in your own worklog;
      fix the progress table to match the evidence.

## Always-stop (every autonomy tier — DISCIPLINE.md §4)

Ask the user before: destructive/irreversible operations · credentials or real
external side-effects · acting over a valid flag · proceeding when ownership
is unanswerable. `supervised-delivery` changes nothing here: it authorizes a
whitelisted push and a ready-for-review PR, never a merge, a tag, a release or a
deploy. A user's explicit stop overrides any autonomy setting; log
mode switches in the journal.
