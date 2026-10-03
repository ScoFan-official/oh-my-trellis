# mp-trellis-pack

A public **asset pack + distribution hub** that fuses three ecosystems —
[mattpocock/skills](https://github.com/mattpocock/skills),
[Everything Claude Code](https://github.com/davila7/claude-code-templates) (ECC),
and [Trellis](https://github.com/mindfold-ai/Trellis) — and ships them to
**22 agent platforms** from one repo.

## What's inside (1,740+ assets)

| Layer | Contents | How it ships |
| --- | --- | --- |
| `marketplace/` | Trellis spec-registry template (`agent-workflow`) — the Trellis-backend contract for mp skills | `trellis init --registry` |
| `skills/` | **38 skills**: `mp-trellis-bridge` + all of mattpocock's (engineering 19, productivity 7, misc 4, in-progress 6, +1) | `npx skills add` |
| `catalog/` | Full mirror: **mp docs + claude-plugin + .agents**, and ECC's complete components — **889 skills, 422 agents, 288 commands, 104 MCPs**, plus hooks/loops/mods/settings/sandbox | `scripts/install.py` |

## Three install channels

### 1. Trellis spec registry — the contract

```bash
trellis init --registry gh:ScoFan-official/mp-trellis-pack/marketplace --template agent-workflow --append
```

Installs `agents/` + `guides/` specs into `.trellis/spec/` with `paths:`-scoped
injection: the tracker contract (spec → task dir, ticket → child task,
triage → `meta.triage`, wayfinder → `map.md`), triage roles, domain docs, and
the mp×Trellis integration guide.

### 2. skills CLI — the core skill set

```bash
npx skills add ScoFan-official/mp-trellis-pack --agent <platform> --copy
```

Installs all 38 skills for any supported platform (`devin`, `codex`, `claude`,
…). `mp-trellis-bridge` bootstraps the spec contracts on first load.

### 3. install.py — the full catalog, per platform

```bash
# inventory
python scripts/install.py --list

# everything ECC+mp, shaped for your platform
python scripts/install.py --platform codex --target /path/to/repo
python scripts/install.py --platform devin --target /path/to/repo
python scripts/install.py --platform zcode --target /path/to/repo

# surgical installs
python install.py --platform codex --target . \
  --component "ecc:agents/security/*" "ecc:commands/git-workflow/commit" "mp:engineering/tdd"

# just the recommended core (bridge + mp main skills)
python install.py --platform zcode --target . --only-core

# preview
python install.py --platform claude --target . --dry-run
```

## Platform support (22)

Every asset type lands in the platform's native location and format:

| Platform | skills | sub-agents | commands | mcp |
| --- | --- | --- | --- | --- |
| claude / cursor / codebuddy / droid / qoder / pi / gemini | native dir | md | md commands | json |
| opencode | `.opencode/skills` | md + `permission:` | md | json |
| **codex** | `.agents/skills` | **`.toml` + `developer_instructions`** | wrapped as skills | `config.toml` snippets |
| kiro | `.kiro/skills` | json | wrapped as skills | json |
| copilot | `.github/skills` | `*.agent.md` | `*.prompt.md` | json |
| **devin** | `.devin/skills` | — (inline) | `.devin/workflows/` | json |
| **zcode** | `.zcode/skills` | md (no `tools:`) | md | json |
| kilo / antigravity | native dir | — (inline) | workflows | json |
| omp / reasonix / trae / grok / kimi / snow / dsh | native dir | md (conv.) | md (conv.) | json |

`verified` platforms follow Trellis's documented file locations; the rest use
convention-based guesses (marked in `scripts/platforms.py` and `manifest.json`)
— treat their agent/command output as drafts to review.

## Repo layout

```
marketplace/            # Trellis spec registry (index.json + agent-workflow)
skills/                 # npx-skills surface: bridge + all mp skills
catalog/
├── manifest.json       # every asset → per-platform target paths
├── upstream.json       # pinned upstream SHAs
├── ATTRIBUTION.md
├── mattpocock/         # skills(4 dirs) + docs + .claude-plugin + .agents
└── ecc/                # skills agents commands hooks mcps loops mods settings sandbox
scripts/
├── platforms.py        # 22-platform location table (single source of truth)
├── install.py          # materialize catalog → any platform, any subset
├── build_manifest.py   # regenerate manifest.json
└── sync_upstream.py    # re-vendor upstreams (--check = drift report)
```

## Not ported (by design)

ECC `hooks/`, `settings/`, `loops/`, `mods/`, `sandbox/` stay in `catalog/` as
reference — they're Claude-Code-specific (hook JSON, settings.json, sandboxed
bash); porting means rewriting per platform. mattpocock's `.claude-plugin/` is
preserved so Claude users can also add his native marketplace directly.

## Updating

```bash
python scripts/sync_upstream.py --check   # see if upstreams moved
python scripts/sync_upstream.py           # re-vendor catalog/
python scripts/build_manifest.py          # refresh manifest
npx skills update                          # colleague-side skill updates
```

Installed specs remain project-owned (Trellis model); catalog files are the
pack's vendored copies — don't patch `catalog/` in place, sync overwrites.

## Requirements

- Python 3.8+, git, `npx skills` for channel 2
- Trellis repo only required for channel 1 (spec registry)
