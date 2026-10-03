# Template: agent-workflow

Trellis spec template that makes [mattpocock/skills](https://github.com/mattpocock/skills) treat the Trellis task system as its issue tracker.

## What installs

| Spec file | Injected when the agent touches |
| --- | --- |
| `agents/issue-tracker.md` | `.trellis/tasks/`, `.scratch/` — the noun/verb contract: spec → task dir, ticket → child task + `blocked_by` meta, triage role → task meta, wayfinder map → parent `map.md` |
| `agents/triage-labels.md` | `.scratch/`, `.trellis/tasks/` — the five-role vocabulary and its `meta.triage` mapping |
| `agents/domain.md` | `GLOSSARY.md`, `docs/adr/`, `.trellis/spec/` — single-context domain doc conventions |
| `guides/mp-integration.md` | pull only — phase map, lane rules, skill precedence |

Files carry `paths:` frontmatter for Trellis dynamic spec loading; without that feature they behave as normal pull-mode specs.

## Requires

- mattpocock skills: `npx skills add mattpocock/skills --agent <platform> --copy`
- The bridge skill for lane rules + bootstrapping: `npx skills add ScoFan-official/mp-trellis-pack --agent <platform> --copy`

## After install

Specs are yours. Edit them to match the repo — the template is a starting point, not a live remote wiki.
