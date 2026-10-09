# Template: agent-workflow

Trellis spec template that points [mattpocock/skills](https://github.com/mattpocock/skills) at the Trellis task system as its issue tracker.

## What installs

| Spec file | Reached via |
| --- | --- |
| `agents/index.md` | injected by the session-start hook — the entry point; lists the contracts below |
| `agents/issue-tracker.md` | `agents/index.md` — the noun/verb contract: spec → task dir, ticket → child task + `blocked_by`, triage role → task meta, wayfinder map → parent `map.md` |
| `agents/triage-labels.md` | `agents/index.md` — the five-role vocabulary and its `meta.triage` mapping |
| `agents/domain.md` | `agents/index.md` — single-context domain doc conventions |
| `agents/frontend-craft.md` | `agents/index.md` — impeccable binding (PRODUCT/DESIGN → `.trellis/spec/`) + the mechanical `## Design review` gate |
| `guides/mp-integration.md` | `guides/index.md` (project-owned; the bridge appends the pointer) — phase map, lane rules, skill precedence |

Delivery is index-driven: the session-start hook injects each package's
`index.md`; agents read the contracts the index lists. No per-file path globs
are parsed — the specs are pull-mode docs.

## Requires

- mattpocock skills: `npx skills add mattpocock/skills --agent <platform> --copy`
- The bridge skill for lane rules + bootstrapping: `npx skills add ScoFan-official/oh-my-trellis --agent <platform> --copy`

## After install

Specs are yours. Edit them to match the repo — the template is a starting point, not a live remote wiki.
