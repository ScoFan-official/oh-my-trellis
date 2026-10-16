#!/usr/bin/env python3
"""scope_check.py — mechanical gate for cleanup tickets: scope prefix + line count.

Checks two things:
  1. Every changed path must hit the declared scope prefix (out-of-scope = FAIL).
  2. A changed file over the threshold (default 800 lines) = FAIL;
     --oversize report downgrades it to a warning.

--scan-oversize is a scan mode: it enumerates all over-threshold files under
the scope prefix and reports without failing.

Usage:
  python scope_check.py --scope src/foo [--scope src/bar] [--max-lines 800]
                        [--base <ref>] [--oversize fail|report]
                        [--scan-oversize] [--json]

Exit codes: 0 = PASS / report-only; 1 = violations; 2 = git call failed.
Stdlib only, no third-party dependencies. Output is ASCII on purpose so the
gate stays readable on GBK consoles.
"""

import argparse
import json
import os
import subprocess
import sys

SKIP_DIRS = {
    ".git", ".trellis", ".devin", ".claude", ".cursor", ".codex",
    "node_modules", "dist", "build", ".next", "out",
    "__pycache__", ".venv", "venv", ".idea", ".vscode",
}


def run_git(args):
    proc = subprocess.run(
        ["git"] + args, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        sys.stderr.write("git %s failed: %s\n" % (" ".join(args), proc.stderr.strip()))
        sys.exit(2)
    return proc.stdout


def norm(path):
    p = path.replace("\\", "/")
    if p.startswith("./"):
        p = p[2:]
    return "" if p in (".", "") else p


def changed_paths(base):
    if base:
        out = run_git(["diff", "--name-only", base])
        return [norm(p) for p in out.splitlines() if p.strip()]
    out = run_git(["status", "--porcelain"])
    paths = []
    for line in out.splitlines():
        if not line.strip():
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        path = path.strip().strip('"')
        if path:
            paths.append(norm(path))
    return paths


def in_scope(path, scopes):
    return any(not s or path == s or path.startswith(s + "/") for s in scopes)


def disp(scopes):
    return ", ".join(s or "." for s in scopes)


def line_count(path):
    try:
        with open(path, "rb") as fh:
            data = fh.read()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    return len(data.splitlines())


def scan_oversize(scopes, max_lines):
    hits = []
    for scope in scopes:
        root = scope if os.path.isdir(scope) else os.path.dirname(scope) or "."
        if not os.path.isdir(root):
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                path = norm(os.path.join(dirpath, name))
                if not in_scope(path, scopes):
                    continue
                n = line_count(path)
                if n is not None and n > max_lines:
                    hits.append((path, n))
    hits.sort(key=lambda item: -item[1])
    return hits


def main():
    parser = argparse.ArgumentParser(
        description="cleanup-ticket scope and line-count gate")
    parser.add_argument("--scope", action="append", required=True,
                        help="scope prefix, repo-relative; repeatable")
    parser.add_argument("--max-lines", type=int, default=800,
                        help="per-file line threshold (default: 800)")
    parser.add_argument("--base", default=None,
                        help="baseline git ref; default = uncommitted worktree")
    parser.add_argument("--oversize", choices=["fail", "report"], default="fail",
                        help="handling of over-threshold files in the diff "
                             "(default: fail)")
    parser.add_argument("--scan-oversize", action="store_true",
                        help="scan mode: list all over-threshold files under "
                             "the scope; never fails")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    scopes = [norm(s).rstrip("/") for s in args.scope]
    result = {"scopes": scopes, "max_lines": args.max_lines, "ok": True,
              "out_of_scope": [], "oversize_edits": [], "oversize_scan": []}

    if args.scan_oversize:
        result["oversize_scan"] = [
            {"file": p, "lines": n} for p, n in scan_oversize(scopes, args.max_lines)
        ]
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            if not result["oversize_scan"]:
                print("PASS scan-oversize: no file over %d lines under %s"
                      % (args.max_lines, disp(scopes)))
            for item in result["oversize_scan"]:
                print("OVERSIZE %6d  %s" % (item["lines"], item["file"]))
            if result["oversize_scan"]:
                print("REPORT %d file(s) over %d lines -- split plan first, no edits"
                      % (len(result["oversize_scan"]), args.max_lines))
        return 0

    paths = changed_paths(args.base)
    result["changed"] = paths
    for path in paths:
        if not in_scope(path, scopes):
            result["out_of_scope"].append(path)
        elif os.path.isfile(path):
            n = line_count(path)
            if n is not None and n > args.max_lines:
                result["oversize_edits"].append({"file": path, "lines": n})

    fail = bool(result["out_of_scope"])
    if args.oversize == "fail" and result["oversize_edits"]:
        fail = True
    result["ok"] = not fail

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for path in result["out_of_scope"]:
            print("SCOPE-VIOLATION  %s  (outside %s)" % (path, disp(scopes)))
        for item in result["oversize_edits"]:
            tag = "OVERSIZE-EDIT" if args.oversize == "fail" else "oversize-warn"
            print("%s  %s  %d lines > %d -- split plan first, no edits"
                  % (tag, item["file"], item["lines"], args.max_lines))
        if fail:
            print("FAIL %d scope violation(s), %d oversize edit(s)"
                  % (len(result["out_of_scope"]),
                     len(result["oversize_edits"])))
        else:
            print("PASS %d changed file(s) within scope %s"
                  % (len(paths), disp(scopes)))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
