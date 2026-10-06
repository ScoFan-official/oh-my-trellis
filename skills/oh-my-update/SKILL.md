---
name: oh-my-update
description: "Update the oh-my-trellis stack — fork CLI, .trellis/ templates, installed skills and .trellis/spec/ contracts — to the latest ScoFan-official releases. Load when the user asks to update oh-my-trellis, check for a new version, or 更新 trellis 环境."
---

# oh-my-trellis update

Update this project's oh-my-trellis stack: the global `oh-my-trellis`/`trellis`
CLI, `.trellis/` templates, installed skills and `.trellis/spec/` — in that
order, with a confirmation gate before anything changes. (On Devin this same
flow ships as the `/oh-my-update` workflow.)

## Step 1: Check versions

```bash
trellis --version
gh api repos/ScoFan-official/oh-my-trellis/releases
```

CLI releases live on `ScoFan-official/oh-my-trellis` tagged `cli-v<ver>`
(e.g. `cli-v0.6.17-ohmy.2`). The pack's own `vX.Y.Z` releases share the same
list — filter `tag_name` on the `cli-v` prefix and pick the newest match.
Do NOT use `/releases/latest`: it can resolve to a pack release.

Record:

- `current` = the version `trellis --version` prints (e.g. `0.6.17-ohmy.2`)
- `latest` = the newest `cli-v*` `tag_name`, minus the `cli-v` prefix
  (e.g. `0.6.17-ohmy.2`)
- `tarball` =
  `https://github.com/ScoFan-official/oh-my-trellis/releases/download/cli-v<latest>/oh-my-trellis-<latest>.tgz`
  (or the `.tgz` asset's `browser_download_url` from the release response)

If `gh` is unavailable or the API call fails, stop and report — do not guess
the latest version.

Also check pack freshness (skills layer): the skills CLI lock records the
hash this repo's skills were installed at — inspect `skills-lock.json`
(project root) and diff it against the remote pack state; `npx skills`
reports the same drift when you ask it to update. If the lock's recorded
source/hash is behind `ScoFan-official/oh-my-trellis@main` (or the pack's
latest pack `v*` tag / `VERSION`), the skills layer is stale too.

## Step 2: Summarize the update

Before touching anything, present:

- version delta: `<current> → <latest>` (or "already up to date" — then stop,
  unless the pack layer is stale)
- pack delta: installed skills hash vs remote, if stale
- changelog summary: the first section of the release `body`, condensed to a
  few bullets
- affected layers: Trellis templates (`.trellis/`), skills (the platform's
  skills dir), specs (`.trellis/spec/`)

## Step 3: Confirm

Ask the user to confirm the update. Do not proceed on silence; on a "no",
stop and report nothing was changed.

## Step 4: Apply, in order

```bash
# 0. one-time only: if upstream @mindfoldhq/trellis is globally installed it
#    must be removed first — our package owns the `trellis` bin.
#    `npm ls -g @mindfoldhq/trellis` → if present: `npm rm -g @mindfoldhq/trellis`
npm i -g <tarball>   # the release .tgz asset URL from Step 1
trellis update       # refresh .trellis/ + platform managed templates
npx skills add ScoFan-official/oh-my-trellis --agent <platform> --copy
trellis init -r gh:ScoFan-official/oh-my-trellis -t agent-workflow --append
```

`<platform>` is this agent's platform id as the skills CLI knows it
(`devin`, `codex`, `claude`, `cursor`, …).

Run each step only if the previous succeeded; on failure stop and report
which step failed.

## Step 5: Report

- old version → new version (`trellis --version` again to verify)
- per-layer result: CLI / Trellis templates / skills / specs —
  updated | skipped | failed
- leftover `.new` files: `find . -name '*.new'` — list them and remind the
  user to diff-and-merge
