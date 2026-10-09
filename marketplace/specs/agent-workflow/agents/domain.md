---
name: agent-domain-docs
description: "Domain vocabulary conventions: single-context GLOSSARY.md + GLOSSARY-MAP.md + docs/adr/, created lazily by the domain-modeling skill. Consulted when writing specs, ADRs or glossary entries."
---

# Domain docs layout

Single-context project — one shared domain vocabulary.

## Files

- **`GLOSSARY.md`** (repo root) — the ubiquitous language. Domain terms used in specs, tickets and code comments must come from here; new terms are added here first.
- **`GLOSSARY-MAP.md`** (repo root, optional) — maps legacy/alternate names to canonical terms.
- **`docs/adr/NNNN-title.md`** — architecture decision records. Check ADRs touching the area before proposing implementation decisions.

## Rules for skills

- Specs and tickets must use glossary vocabulary. If a needed term is missing, flag it (or run `/domain-modeling` to extend the glossary) rather than inventing a synonym.
- `GLOSSARY.md` and the first ADR are created **lazily** — by `/domain-modeling` during `/grill-with-docs` or `/improve-codebase-architecture`, not upfront.
- Before changing domain-related artifacts, consult the glossary and relevant ADRs; absent files mean proceed without creating them.
- ADR numbering: `docs/adr/0001-<slug>.md`, sequential; immutable once accepted — supersede with a new ADR instead of editing.
