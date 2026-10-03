#!/usr/bin/env python3
"""build_manifest.py — scan catalog/ → catalog/manifest.json with per-platform targets."""

import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from platforms import PLATFORMS
from install import discover

def target_paths(a):
    out = {}
    for key, p in PLATFORMS.items():
        t = a["type"]
        if t == "skill":
            out[key] = f'{p["skills"]}/{a["name"]}/'
        elif t == "agent":
            out[key] = f'{p["agents"][0]}/{a["name"]}.*' if p["agents"] else "n/a (no sub-agent primitive)"
        elif t == "command":
            out[key] = (f'{p["skills"]}/ecc-{a["name"]}/SKILL.md' if p["commands"][1] == "skill"
                        else f'{p["commands"][0]}/ecc[-/]{a["name"]}.*')
        elif t == "mcp":
            out[key] = p["mcp"][0]
    return out

def main():
    assets = discover()
    manifest = {
        "version": 1,
        "sources": {
            "mp":  {"repo": "mattpocock/skills", "license": "MIT"},
            "ecc": {"repo": "davila7/claude-code-templates", "license": "MIT"},
            "pack": {"repo": "ScoFan-official/mp-trellis-pack"},
        },
        "counts": {},
        "assets": [
            {**{k: a[k] for k in ("id", "type", "source", "category", "name")},
             "path": str(a["path"].relative_to(ROOT)).replace("\\", "/"),
             "targets": target_paths(a)}
            for a in assets
        ],
    }
    from collections import Counter
    manifest["counts"] = dict(Counter(f'{a["source"]}/{a["type"]}' for a in assets))
    out = ROOT / "catalog" / "manifest.json"
    out.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"manifest: {len(assets)} assets, {out.stat().st_size//1024} KB")

if __name__ == "__main__":
    main()
