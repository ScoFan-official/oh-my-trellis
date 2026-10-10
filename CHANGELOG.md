# Changelog

All notable changes to the oh-my-trellis pack are documented here.

Versioning: semver `X.Y.Z` — **major** = contract/layout breaking changes
(spec registry shape, asset IDs, platform tables), **minor** = new
skills/assets/templates added, **patch** = fixes to existing content.
`VERSION` at the repo root is the source of truth; each release is tagged
`vX.Y.Z`.

## Unreleased

Review follow-up (10-10): the delivery text corrected to match the mechanism the
`/code-review` axis found, plus the runner's two new behaviors documented.

- `skills/trellis-run/SKILL.md`: the claim "the repo you launch from is never
  written to" was **false** — a ticket that hits the fail threshold is marked
  `triage=ready-for-human` on the launching copy (its worktree is already gone,
  and that copy is the board a human reads next). Rewritten with the exception
  named instead of an absolute denied by the next bullet in the same file.
- Same file: new stop condition `always_stop` (a board file or credential-shaped
  path landed in a commit on the ticket branch — the line halts before verify,
  push and PR); the commit-path check now runs twice against one authority
  (`task.py check-commit`, CLAI-10) so an agent committing by hand gets the same
  answer; the worker's second clock (`channel.worker_guard.idle_timeout`, default
  5 min, re-armed by every event) and why `max_live_workers` does not apply.
- `guides/mp-integration.md`: same zero-write claim narrowed, `always-stop`
  added to the stop-line list.
- Fork-side prerequisites for this text (not pack content): bounded tree-kill in
  `run-verify`, the idle clock, and CLAI-10 `task.py check-commit` — pack `main`
  describes them; `cli-v0.6.18-ohmy.2` will ship them.

Slice-7 contract sync: the runner era (`trellis run`, CLAI-8) gets an operator
shell skill, and the delivery text now describes tiers that exist.

- `skills/trellis-run/` — **new**. Thin-shell operator skill for
  `trellis run`: when the loop is the right tool, what the tier and
  `delivery.auto_push_refs` must already allow, what each stop reason
  (`cycle` / `fail_threshold` / `push_refused` / `delivery_deferred` /
  `no_grabbable_ticket`) asks of you, and why the run ledger is a trace rather
  than a reconciliation source. Protocol text stays in the consuming repo.
- Skill count 41 → 42 (both READMEs: install line, quick-start table, skill
  table).
- `guides/mp-integration.md`: new unattended lane — per-ticket worktree, worker,
  verify, `delivery-gate` before any remote touch, the four stop lines, and the
  two properties that matter (the loop never writes to the launching repo;
  PR ≠ delivery, only a human merge closes the board row).
- `skills/trellis-domains/`: always-stop is now phrased for three tiers
  (`gated` / `hands-off` / `supervised-delivery`), with the explicit note that
  the new tier authorizes a whitelisted push and a ready-for-review PR — never a
  merge, tag, release or deploy.
- Prerequisite landed fork-side (not pack content): CLAI-8
  `task.py delivery-gate` + the third tier in `.trellis/config.yaml`, D5
  `trellis run`, and D8's platform-resolved writer identity. The pack describes
  them; the fork CLI ships them.

Slice-5 contract alignment: the agent-workflow template now describes the
delivery mechanism that actually exists (index-driven spec injection), and the
tracker/frontend contracts match the fork CLI's mechanical gates.

- Both READMEs + registry descriptions: the "dynamic spec loading" /
  "path-scoped spec injection" claim is replaced with what the session-start
  hook really does — inject each package's `index.md`; the agent reads the
  contracts those indexes list. Specs are pull-mode docs.
- `marketplace/specs/agent-workflow/guides/index.md` removed — the shipped
  stub could overwrite a project-owned guides index. The bridge skill now
  ensures the project's own `guides/index.md` carries the `mp-integration.md`
  pointer (append or create-iff-missing; never rewrite).
- `agents/issue-tracker.md`: frontier is the `task.py frontier` command; the
  blocking edge is the formal `task.json` `blocked_by` field written via
  `set-meta` (the legacy `--meta blocked_by=` create path still reads for
  compatibility); wayfinding Blocking/Frontier bullets aligned.
- `agents/frontend-craft.md`: `paths:` frontmatter removed; frontend-ness is
  `meta.frontend` (explicit override) else best-effort branch-diff detection;
  the design-review gate is mechanical (`archive` refuses) per fork CLAI-7.
- `agents/{triage-labels,domain}.md`: dead `paths:` frontmatter removed.
- `skills/mp-trellis-bridge/templates/`: all five copies resynced with the
  agent contracts; install step now also wires the guides-index pointer.
- `skills/implement-spec/`: points at `task.py frontier` as the mechanical
  frontier on Trellis repos.
- `guides/mp-integration.md`: phase map reflects the frontier step, the
  formal `blocked_by` field, index-driven delivery and the archive-refusal
  design gate.

## 1.2.0 — 2026-10-07

- `skills/trellis-domains/` — thin-shell operator skill for the
  `.trellis/domains/` domain layer shipped by fork `cli-v*` template
  releases: routes 归口 / 旗 / 接手 / 收工 / 对账 situations to the
  repo-internal authority texts (`DISCIPLINE.md`, `WORKLOG-PROTOCOL.md`,
  `REGISTRY.md`, per-board artifacts) and carries checklist-level indexes
  only — protocol text lives in the consuming repo, never duplicated here.

## 1.1.0

CLI distribution moves in-house — this repo is now the single user-facing
release surface for both the pack and the `oh-my-trellis` CLI.

- `.github/workflows/cli-release.yml` — new pipeline: a `cli-v<ver>` tag push
  clones the public fork (`ScoFan-official/trellis`) at the matching `v<ver>`
  tag, builds `oh-my-trellis` with pnpm, packs the tarball and publishes it as
  a `cli-v*` release asset here. Pack releases (`vX.Y.Z`) and CLI releases
  (`cli-v*`) now share one releases page; `cli-v*` tags are not pack releases.
- `skills/oh-my-update` + both READMEs repointed: version checks filter
  `cli-v*` tags on `repos/ScoFan-official/oh-my-trellis/releases` (never
  `/releases/latest` — pack releases share the list), and install URLs moved
  to `releases/download/cli-v<ver>/oh-my-trellis-<ver>.tgz`. Fork-hosted CLI
  releases are deprecated.
- Requires fork `0.6.17-ohmy.2` or later for the matching update-side fix
  (same repointing + `X.Y.Z-ohmy.N` >= `X.Y.Z` comparison).

## 1.0.0

First versioned release of the pack.

Already in the pack:

- `skills/` — the `npx skills` install surface: `mp-trellis-bridge` plus the
  full mattpocock collection (engineering / productivity / misc / in-progress)
  plus `impeccable` — 39 default skills.
- `catalog/` — 1,741 vendored components from mattpocock/skills,
  Everything-Claude-Code and impeccable (`INDEX.md`, `manifest.json`,
  `upstream.json`, `ATTRIBUTION.md`).
- `marketplace/` — the Trellis spec registry channel (`index.json` +
  `agent-workflow` template: `agents/` + `guides/` spec contracts).
- `scripts/` — `platforms.py` (22-platform location table), `install.py`
  (catalog → platform-native materializer), `build_manifest.py`,
  `build_index.py`, `sync_upstream.py`.

New in this release:

- `index.json` at the repo root — same registry index as
  `marketplace/index.json` (paths are repo-root-relative), so
  `-r gh:ScoFan-official/oh-my-trellis` resolves the registry directly,
  alongside `gh:ScoFan-official/oh-my-trellis/marketplace`.
- `skills/oh-my-update/` — skill form of the update flow (same logic as the
  fork's `.devin/workflows/oh-my-update.md`): check the global
  oh-my-trellis/trellis CLI against `ScoFan-official/trellis` releases, check
  pack freshness via the skills lock, summarize, confirm, then apply
  CLI → `trellis update` → `npx skills add` → spec `--append`, in order.
- `VERSION` + this changelog — the pack now releases as tagged semver,
  consumed alongside the `ScoFan-official/trellis` fork CLI
  (`0.6.17-ohmy.N` release line).
