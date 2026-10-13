# voice ！ STC + ASD-STE100 lint toolchain

Vendored linters for the repo communication standard (`.trellis/spec/agents/voice.md`).

- `stc/` ！ @daimonia/stc `tools/` tree (MIT; `stc check` for Chinese). Requires **Node 18+**.
- `ste/` ！ `asd-ste100-skill` `ste-lint.py` (MIT; Python 3 stdlib, zero deps).
- `voice_lint.py` ！ unified wrapper: `--changed` (hard-fail) / `--all` (advisory) / `--strict-all` / file args. Install to `.trellis/scripts/voice_lint.py`; vendored trees mirror to `.trellis/scripts/voice/{stc,ste}/`.

Blocking: stc `error` + ste `advisory-free`. Excludes `.trellis/tasks/archive/`, `.trellis/workspace/`, `.scratch/`, pack submodule itself.
