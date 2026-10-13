#!/usr/bin/env python3
"""voice_lint.py — STC (中文) + ASD-STE100 (English) unified lint wrapper.

Usage:
    python .trellis/scripts/voice_lint.py --changed     # git diff vs HEAD (hard-fail)
    python .trellis/scripts/voice_lint.py --all         # every tracked *.md (advisory, exit 0)
    python .trellis/scripts/voice_lint.py --strict-all  # every tracked *.md (hard-fail)
    python .trellis/scripts/voice_lint.py FILE ...      # explicit files (hard-fail)

Blocking findings: stc level `error`, ste level `advisory-free`.
Non-blocking findings are still printed. Exit 1 on blocking findings in
hard-fail modes; --all always exits 0.

Routing: each non-code line is classified CJK (contains a CJK char) or English
(contains an ASCII letter). CJK lines go to `stc check`, English lines to
`ste-lint.py`; the other lines are blanked to preserve line:col positions.
Code fences and YAML frontmatter are masked from both linters.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STC_CLI = os.path.join(REPO_ROOT, ".trellis", "scripts", "voice", "stc", "tools", "cli.mjs")
STE_LINT = os.path.join(REPO_ROOT, ".trellis", "scripts", "voice", "ste", "scripts", "ste-lint.py")

EXCLUDE_PATTERNS = (
    ".trellis/tasks/archive/",
    ".trellis/workspace/",
    ".trellis/.runtime/",
    ".scratch/",
    "tools/mp-trellis-pack/",
    "node_modules/",
)

INSTRUCTION_PATH_HINTS = (
    ".trellis/agents/",
    ".trellis/spec/",
    ".devin/",
    ".agents/",
    ".codex/",
    ".claude/",
    ".cursor/",
    ".trellis/domains/",
)
INSTRUCTION_BASENAMES = {"AGENTS.md", "CLAUDE.md", "SKILL.md", "GLOSSARY.md", "RULE.md"}
DOC_PATH_HINTS = (".trellis/tasks/", "docs/")

CJK_RE = re.compile(r"[一-鿿㐀-䶿豈-﫿]")
ASCII_LETTER_RE = re.compile(r"[A-Za-z]")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def to_posix(path):
    return path.replace("\\", "/")


def is_excluded(posix_path):
    return any(p in posix_path for p in EXCLUDE_PATTERNS)


def stc_profile(posix_path):
    base = posix_path.rsplit("/", 1)[-1]
    if base in INSTRUCTION_BASENAMES:
        return "for-instruction-writing"
    if any(h in posix_path for h in INSTRUCTION_PATH_HINTS):
        return "for-instruction-writing"
    if any(h in posix_path for h in DOC_PATH_HINTS):
        return "for-document"
    return "for-document"


def collect_files(args):
    """Return (files, hard_fail) from argv."""
    if "--changed" in args:
        out = subprocess.run(
            ["git", "diff", "--name-only", "HEAD", "--", "*.md"],
            cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8",
        ).stdout.splitlines()
        out += subprocess.run(
            ["git", "ls-files", "--others", "--exclude-standard", "--", "*.md"],
            cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8",
        ).stdout.splitlines()
        return sorted(set(out)), True
    if "--all" in args or "--strict-all" in args:
        out = subprocess.run(
            ["git", "ls-files", "--", "*.md"],
            cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8",
        ).stdout.splitlines()
        return sorted(set(out)), "--strict-all" in args
    files = [a for a in args if not a.startswith("--")]
    return files, True


def mask_file(path):
    """Split a markdown file into (cjk_text, en_text) with line positions kept.

    Neutral lines (no CJK, no ASCII letters) are blanked in both streams.
    Frontmatter and fenced code blocks are blanked in both streams.
    """
    try:
        text = open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError):
        return None, None
    lines = text.splitlines()
    cjk_lines, en_lines = [], []
    in_fence = False
    in_frontmatter = False
    for i, line in enumerate(lines):
        if i == 0 and line.strip() == "---":
            in_frontmatter = True
            cjk_lines.append("")
            en_lines.append("")
            continue
        if in_frontmatter:
            cjk_lines.append("")
            en_lines.append("")
            if i > 0 and line.strip() in ("---", "..."):
                in_frontmatter = False
            continue
        if FENCE_RE.match(line):
            in_fence = not in_fence
            cjk_lines.append("")
            en_lines.append("")
            continue
        if in_fence:
            cjk_lines.append("")
            en_lines.append("")
            continue
        if CJK_RE.search(line):
            cjk_lines.append(line)
            en_lines.append("")
        elif ASCII_LETTER_RE.search(line):
            cjk_lines.append("")
            en_lines.append(line)
        else:
            cjk_lines.append("")
            en_lines.append("")
    cjk_text = "\n".join(cjk_lines)
    en_text = "\n".join(en_lines)
    return (cjk_text if CJK_RE.search(cjk_text) else "",
            en_text if ASCII_LETTER_RE.search(en_text) else "")


def run_stc(path, text, profile):
    """Run stc check on `text` via a temp file; return finding dicts."""
    if not shutil.which("node"):
        print("voice_lint: node not found — STC checks skipped", file=sys.stderr)
        return []
    if not os.path.isfile(STC_CLI):
        print(f"voice_lint: stc not vendored at {STC_CLI}", file=sys.stderr)
        return []
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", prefix="voice_lint_", delete=False, encoding="utf-8"
    )
    try:
        tmp.write(text)
        tmp.close()
        proc = subprocess.run(
            ["node", STC_CLI, "check", "--json", "--profile", profile, tmp.name],
            capture_output=True, text=True, encoding="utf-8", cwd=REPO_ROOT,
        )
        if not proc.stdout.strip():
            if proc.stderr.strip():
                print(f"voice_lint: stc stderr: {proc.stderr[:200]}", file=sys.stderr)
            return []
        data = json.loads(proc.stdout)
        findings = []
        for f in data.get("files", []):
            for issue in f.get("issues", []):
                findings.append({
                    "file": path,
                    "line": issue.get("line", 0),
                    "col": issue.get("col", 1),
                    "rule": f"stc/{issue.get('rule', '?')}",
                    "level": "hard" if issue.get("level") == "error" else "advisory",
                    "message": issue.get("message", ""),
                })
        return findings
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


def run_ste(path, text, disable_long_sentence):
    """Run ste-lint.py on `text` via stdin; return finding dicts."""
    if not os.path.isfile(STE_LINT):
        print(f"voice_lint: ste-lint not vendored at {STE_LINT}", file=sys.stderr)
        return []
    cmd = [sys.executable, STE_LINT, "--json"]
    if disable_long_sentence:
        cmd += ["--disable", "long-sentence"]
    proc = subprocess.run(
        cmd, input=text, capture_output=True, text=True, encoding="utf-8", cwd=REPO_ROOT,
    )
    out = proc.stdout.strip()
    if not out:
        return []
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return []
    if isinstance(data, dict):
        items = data.get("violations", data.get("findings", []))
    else:
        items = data
    findings = []
    for f in items:
        findings.append({
            "file": path,
            "line": f.get("line", 0),
            "col": f.get("col", 1),
            "rule": f"ste/{f.get('rule', '?')}",
            "level": "hard" if f.get("level") == "advisory-free" else "advisory",
            "message": f.get("message", ""),
        })
    return findings


def main(argv):
    if not argv or "--help" in argv:
        print(__doc__)
        return 0
    files, hard_fail = collect_files(argv)
    files = [f for f in files if f.endswith(".md") and not is_excluded(to_posix(f))]
    if not files:
        print("voice_lint: no target files")
        return 0

    all_findings = []
    for rel in files:
        posix = to_posix(rel)
        path = os.path.join(REPO_ROOT, rel) if not os.path.isabs(rel) else rel
        if not os.path.isfile(path):
            continue
        cjk_text, en_text = mask_file(path)
        profile = stc_profile(posix)
        if cjk_text:
            all_findings += run_stc(rel, cjk_text, profile)
        if en_text:
            disable = profile == "for-document"
            all_findings += run_ste(rel, en_text, disable)

    all_findings.sort(key=lambda f: (f["file"], f["line"], f["col"]))
    blocking = [f for f in all_findings if f["level"] == "hard"]
    for f in all_findings:
        tag = "" if f["level"] == "hard" else " (advisory)"
        print(f"{f['file']}:{f['line']}:{f['col']} {f['rule']}: {f['message']}{tag}")
    print(
        f"voice_lint: {len(files)} file(s), {len(blocking)} blocking, "
        f"{len(all_findings) - len(blocking)} advisory"
    )
    return 1 if (hard_fail and blocking) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
