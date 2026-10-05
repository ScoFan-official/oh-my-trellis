# Attribution & Provenance

This catalog vendors digital assets from three upstream projects — mattpocock
and ECC are MIT-licensed; impeccable is Apache-2.0 (its `LICENSE` + `NOTICE.md`
are carried per §4). Upstream license files are preserved in each source directory.

| Source | Repo | License | Pinned SHA | Path in catalog |
| --- | --- | --- | --- | --- |
| mattpocock's skills | [mattpocock/skills](https://github.com/mattpocock/skills) | MIT | see `upstream.json` | `mattpocock/` |
| Everything Claude Code | [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) | MIT | see `upstream.json` | `ecc/` |
| Impeccable | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | Apache-2.0 | see `upstream.json` | `impeccable/` |

- `mattpocock/skills/` — all four collections: `engineering`, `productivity`,
  `misc`, `in-progress`, plus his `docs/`, `.claude-plugin/` (native Claude
  marketplace manifests), and `.agents/` meta files.
- `ecc/` — the full `cli-tool/components/` mirror: skills, agents, commands,
  hooks, mcps, loops, mods, settings, sandbox.
- `impeccable/` — the canonical `.agents/skills/impeccable` skill tree
  (SKILL.md + `reference/` + `agents/` + `scripts/`) plus upstream `docs/`.
  Markdown only: the engine binary, harness hooks and browser extension are
  deliberately not vendored — engine-dependent commands point users at
  `npx impeccable install`.

Refresh: `python scripts/sync_upstream.py` (or `--check` to diff only).
Re-running re-copies upstream content; local edits inside `catalog/` will be
overwritten — keep modifications in `skills/` or `marketplace/` instead.
