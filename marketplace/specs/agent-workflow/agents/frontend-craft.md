---
name: frontend-craft
description: "Frontend craft contract: binds the impeccable skill (design commands, PRODUCT.md/DESIGN.md artifacts) to the Trellis pipeline — product truth and the design system live in .trellis/spec/, shape→craft→audit→polish are wired into phases, and frontend tasks cannot verify READY without a Design review section. Consulted whenever frontend files are touched."
---

# Frontend craft: impeccable × Trellis

The `impeccable` skill supplies the design toolchain (24 commands: shape, craft, audit, critique, polish, …). This contract does two things: it binds impeccable's abstract artifacts to `.trellis/` paths — the same trick the issue-tracker contract plays for "the issue tracker" — and it makes the design-review loop **mandatory** for frontend work, not advisory.

## Nouns → where things live

| impeccable noun | Physical form |
| --- | --- |
| `PRODUCT.md` (durable product truth) | `.trellis/spec/product.md` — same schema, keep the `<!-- impeccable:product-schema N -->` marker verbatim |
| `DESIGN.md` (incumbent/emerging visual system) | `.trellis/spec/design-system.md` |
| surface brief (per-surface visitor mode + direction) | `design.md` inside the active Trellis task dir |
| audit/critique findings | `## Design review` section of the task's `implement.md` |
| `.impeccable/` (engine state: `config.json` `buildPath`, `live/`, `surfaces/`) | stays at project root, only exists when the engine is installed (see *Engine boundary*). Without the engine, record a chosen `buildPath` as a `## Workflow defaults` line in `design-system.md` instead |

Never write `PRODUCT.md` or `DESIGN.md` at repo root — that creates a second authority. When impeccable's own references name those paths, this table wins.

## Bootstrap — replaces `/impeccable init`

Before the first frontend change in a repo, and whenever a frontend task starts while `.trellis/spec/product.md` is missing:

1. Follow the vendored interview in the impeccable skill's `reference/init.md` — explore first, ask only for material gaps (users/jobs, purpose/positioning, durable constraints, evidence), at most three focused questions per round.
2. Write the confirmed record to `.trellis/spec/product.md` using the upstream template (Platform / Users / Product Purpose / Positioning / Operating Context / Capabilities and Constraints / Brand Commitments / Evidence on Hand / Product Principles / Accessibility & Inclusion). Visual direction is **not** captured here — it belongs to the task's `design.md` or `design-system.md`.
3. If an incumbent visual system exists and no `design-system.md` yet, offer the `document` command's flow to record it — same target rule applies.

Do not run this bootstrap inside an unrelated task without telling the user; record undecided facts as undecided rather than inventing them.

## Phase wiring

| Trellis phase | impeccable command | When it fires |
| --- | --- | --- |
| spec bootstrap | init replacement (above) | first frontend touch without `spec/product.md` |
| design (post-PRD, pre-tickets) | `shape` | every frontend task — task discovery + surface concept |
| implement | `craft` (new-work flow) | the build loop for new/redesigned surfaces |
| check | `audit` + `critique` | inside `trellis-check`, before verification |
| finish | `polish` | after check passes, before `task.py archive` |

The other 18 commands (`bolder`, `quieter`, `distill`, `harden`, `onboard`, `animate`, `colorize`, `typeset`, `layout`, `delight`, `overdrive`, `clarify`, `adapt`, `optimize`, `live`, `generate`, `document`, `extract`) stay user-invoked — the phase table names the *floor*, not the ceiling. `init` is covered by the bootstrap above rather than run raw.

Before **any** UI file edit — including small refinements — read the skill's `reference/craft-floor.md` first. It carries the absolute bans (no stock fonts, no gray-on-color, no nested cards…) the detectors can't fully check.

## Engine boundary

The pack vendors markdown only — no binary, no hooks, no browser extension. Two tiers result:

- **Engine-dependent**: the `impeccable context` boot loader, `audit`'s 61 deterministic detector rules, `live`, `generate`, `hooks`, `doctor`, `pin`. These need the upstream engine: `npx impeccable install` in the project (or `~/.impeccable/bin/` present).
- **Markdown-native**: `shape`, `init`, `document`, `extract`, `critique`, `polish` and all Refine/Enhance/Fix commands work as pure guidance; `audit` degrades to LLM-only checks via `reference/audit.md`; `reference/degraded/` holds the official fallbacks.

When the launcher is absent or fails, follow the SKILL.md "Launcher unavailable" path: say so once, read `spec/product.md` + `spec/design-system.md` directly, continue. Missing engine never blocks design work — it only narrows `audit` to judgment calls.

## The gate — design review is not optional

A task is **frontend** when `meta.frontend` says so (`task.py set-meta <dir> frontend true|false` — an explicit value overrides both ways) or, absent that, when the task branch's diff touches one of the frontend suffixes (`.tsx` `.jsx` `.vue` `.svelte` `.astro` `.css` `.scss` `.less` `.html`) or one of the spec files (`.trellis/spec/product.md`, `.trellis/spec/design-system.md`). The diff-based detection is best-effort by design: undetectable frontend-ness (no branch metadata, refs gone) fails open and never blocks archive.

Before a frontend task may record READY in verification (or be archived): its `implement.md` must contain a `## Design review` section recording — which of `audit`/`critique`/`polish` ran (and whether engine or degraded), the findings that mattered, and how each was disposed (fixed / deferred-with-reason / rejected-with-reason). An empty "no findings" entry is valid only if the commands actually ran.

Missing section ⇒ `task.py archive` refuses the task (CLAI-7); treat it as a spec violation, same weight as a failing lint. This is a **contract gate** with mechanical enforcement: `verification-loop`/`trellis-check` honor it before archive, and the CLI backs them after. There is no force flag — if no review applies, write that inside the section (or declare `frontend=false`); the artifact is the point, not the verdict.

If the `impeccable` skill itself is absent from this agent's skills dir, say so and stop — do not improvise a substitute design review. Install it via the pack (`install.py --component imp:impeccable` or the default skill set).
