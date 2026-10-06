# Changelog

All notable changes to the oh-my-trellis pack are documented here.

Versioning: semver `X.Y.Z` — **major** = contract/layout breaking changes
(spec registry shape, asset IDs, platform tables), **minor** = new
skills/assets/templates added, **patch** = fixes to existing content.
`VERSION` at the repo root is the source of truth; each release is tagged
`vX.Y.Z`.

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
