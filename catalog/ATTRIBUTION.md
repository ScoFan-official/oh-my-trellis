# Attribution & Provenance

This catalog vendors digital assets from two upstream projects, both MIT-licensed.
Upstream LICENSE files are preserved in each source directory.

| Source | Repo | Pinned SHA | Path in catalog |
| --- | --- | --- | --- |
| mattpocock's skills | [mattpocock/skills](https://github.com/mattpocock/skills) | see `upstream.json` | `mattpocock/` |
| Everything Claude Code | [davila7/claude-code-templates](https://github.com/davila7/claude-code-templates) | see `upstream.json` | `ecc/` |

- `mattpocock/skills/` — all four collections: `engineering`, `productivity`,
  `misc`, `in-progress`, plus his `docs/`, `.claude-plugin/` (native Claude
  marketplace manifests), and `.agents/` meta files.
- `ecc/` — the full `cli-tool/components/` mirror: skills, agents, commands,
  hooks, mcps, loops, mods, settings, sandbox.

Refresh: `python scripts/sync_upstream.py` (or `--check` to diff only).
Re-running re-copies upstream content; local edits inside `catalog/` will be
overwritten — keep modifications in `skills/` or `marketplace/` instead.
