#!/usr/bin/env python3
"""sync_upstream.py — re-vendor mattpocock/skills + davila7/claude-code-templates
and pbakaus/impeccable into catalog/. Sparse-clones to a temp dir, mirrors the
subtrees, records SHAs.

Usage: python scripts/sync_upstream.py            # full re-sync
       python scripts/sync_upstream.py --check    # only report drift (no writes)
       python scripts/sync_upstream.py --only impeccable   # one source only
"""

import argparse, json, shutil, subprocess, sys, tempfile, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAT = ROOT / "catalog"

# cone-mode sparse-checkout rejects file paths; root files (LICENSE, NOTICE)
# are always checked out anyway
SOURCES = {
    "mattpocock": dict(repo="https://github.com/mattpocock/skills",
                       sparse=["skills", "docs", ".claude-plugin", ".agents"]),
    "ecc": dict(repo="https://github.com/davila7/claude-code-templates",
                sparse=["cli-tool/components"]),
    # canonical skill tree lives at .agents/skills; root .impeccable/ is the
    # repo's own dogfood state, dist/ is release-only — neither is vendored
    "impeccable": dict(repo="https://github.com/pbakaus/impeccable",
                       sparse=[".agents/skills/impeccable", "docs"]),
}


def clone(repo, sparse):
    tmp = Path(tempfile.mkdtemp(prefix="vend-"))
    subprocess.run(["git", "clone", "--depth", "1", "--filter=blob:none",
                    "--sparse", repo, str(tmp / "r")], check=True, capture_output=True)
    subprocess.run(["git", "sparse-checkout", "set", *sparse],
                   cwd=tmp / "r", check=True, capture_output=True)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp / "r",
                         capture_output=True, text=True).stdout.strip()
    return tmp / "r", sha


def fetch_license(repo_api, dest):
    try:
        d = json.load(urllib.request.urlopen(repo_api))
        dest.write_bytes(__import__("base64").b64decode(d["content"]))
    except Exception as e:
        print(f"  ! license fetch failed: {e}")


def sync(name, check):
    src, sha = clone(SOURCES[name]["repo"], SOURCES[name]["sparse"])
    dest = CAT / name
    if check:
        print(f"{name}: upstream @ {sha[:8]}")
        return sha
    dest.mkdir(parents=True, exist_ok=True)
    if name == "mattpocock":
        for sub in ("skills", "docs", ".claude-plugin", ".agents"):
            s = src / sub
            if s.exists(): shutil.copytree(s, dest / sub, dirs_exist_ok=True)
    elif name == "impeccable":
        s = src / ".agents" / "skills"
        if s.exists(): shutil.copytree(s, dest / "skills", dirs_exist_ok=True)
        s = src / "docs"
        if s.exists(): shutil.copytree(s, dest / "docs", dirs_exist_ok=True)
        n = src / "NOTICE.md"  # Apache-2.0 §4(d) — carry attribution notices
        if n.exists(): shutil.copy2(n, dest / "NOTICE.md")
        # keep the shipped default-set copy in lockstep with the vendored one
        shipped = ROOT / "skills" / "impeccable"
        srcskill = dest / "skills" / "impeccable"
        if srcskill.exists():
            if shipped.exists(): shutil.rmtree(shipped)
            shutil.copytree(srcskill, shipped)
    else:
        for s in (src / "cli-tool" / "components").iterdir():
            if s.is_dir(): shutil.copytree(s, dest / s.name, dirs_exist_ok=True)
    fetch_license(f"https://api.github.com/repos/{SOURCES[name]['repo'].split('github.com/')[1]}/contents/LICENSE",
                  dest / "LICENSE")
    (dest / ".upstream-sha").write_text(sha + "\n")
    print(f"{name}: synced @ {sha[:8]}")
    return sha


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--only", choices=sorted(SOURCES), help="sync a single source")
    args = ap.parse_args()
    CAT.mkdir(exist_ok=True)
    names = [args.only] if args.only else list(SOURCES)
    shas = {n: sync(n, args.check) for n in names}
    if not args.check:
        meta = CAT / "upstream.json"
        prev = json.loads(meta.read_text()) if meta.exists() else {}
        prev.update({n: {"repo": SOURCES[n]["repo"], "sha": s} for n, s in shas.items()})
        meta.write_text(json.dumps(prev, indent=2) + "\n")
        print("wrote catalog/upstream.json — run build_manifest.py next")

if __name__ == "__main__":
    main()
