# Agent Workflow Specs

Conventions that wire mattpocock engineering skills into the Trellis task system.

## Files

- `agents/` — machine-facing contracts the skills consume: issue tracker, triage labels, domain docs. Read `agents/index.md` first.
- `guides/mp-integration.md` — how the two workflow systems share phases; lane rules and name-collision precedence.

## When these apply

Any task or ticket produced by `/to-spec`, `/to-tickets`, `/triage`, `/wayfinder`, or `/implement`. The Trellis lifecycle (`task.py`) remains authoritative for status; these specs only define *where* skill artifacts land.
