#!/usr/bin/env python3
"""sync_upstream.py — re-vendor mattpocock/skills + davila7/claude-code-templates
into catalog/. Sparse-clones to a temp dir, mirrors the subtrees, records SHAs.

Usage: python scripts/sync_upstream.py            # full re-sync
       python scripts/sync_upstream.py --check    # only report drift (no writes)
"""

import argparse, json, shutil, subprocess, sys, tempfile, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAT = ROOT / "catalog"

SOURCES = {
    "mattpocock": dict(repo="https://github.com/mattpocock/skills",
                       sparse=["skills", "docs", ".claude-plugin", ".agents", "LICENSE"]),
    "ecc": dict(repo="https://github.com/davila7/claude-code-templates",
                sparse=["cli-tool/components", "LICENSE"]),
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
    args = ap.parse_args()
    CAT.mkdir(exist_ok=True)
    shas = {n: sync(n, args.check) for n in SOURCES}
    if not args.check:
        meta = CAT / "upstream.json"
        meta.write_text(json.dumps(
            {n: {"repo": SOURCES[n]["repo"], "sha": s} for n, s in shas.items()},
            indent=2) + "\n")
        print("wrote catalog/upstream.json — run build_manifest.py next")

if __name__ == "__main__":
    main()
