#!/usr/bin/env python3
"""install.py — materialize catalog assets into a target repo for a given platform.

Examples:
  python install.py --list
  python install.py --platform codex --target ../my-repo
  python install.py --platform devin --target . --only-core --dry-run
  python install.py --platform zcode --target . --type agents --component ecc:security/*
"""

import argparse, json, os, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from platforms import PLATFORMS, MD, MD_AGENT, MD_PERMISSION, MD_ZCODE, TOML, JSON, \
    CMD_MD_NS, CMD_MD_FLAT, CMD_TOML_NS, CMD_PROMPT, CMD_WORKFLOW, CMD_SKILL, \
    MCP_JSON, MCP_TOML

MP_CAT = ROOT / "catalog" / "mattpocock" / "skills"
ECC_CAT = ROOT / "catalog" / "ecc"
NAMESPACE = "ecc"  # namespace prefix for converted commands

# ---------- frontmatter ----------

def parse_frontmatter(text):
    """Minimal YAML-frontmatter subset parser (no pyyaml needed).
    Returns (dict, body). Handles `key: value`, `key: "quoted"`,
    `key: |` / `key: |-` block scalars, and inline comma lists."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not m:
        return {}, text
    fm, body = {}, text[m.end():]
    lines, i, raw = m.group(1).split("\n"), 0, None
    while i < len(lines):
        ln = lines[i]
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", ln)
        if not km:
            i += 1; continue
        k, v = km.group(1), km.group(2).strip()
        if v in ("|", "|-", "|+"):
            block = []
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or lines[i].strip() == ""):
                block.append(lines[i]); i += 1
            fm[k] = "\n".join(block).strip()
            continue
        if v.startswith('"') and v.endswith('"') and len(v) > 1:
            v = v[1:-1].replace('\\"', '"').replace("\\n", "\n")
        elif v.startswith("'") and v.endswith("'") and len(v) > 1:
            v = v[1:-1]
        fm[k] = v
        i += 1
    return fm, body


def q(s):  # TOML/JSON-safe escape of a scalar
    return str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

# ---------- asset discovery ----------

def discover():
    """Every installable asset in the catalog."""
    assets = []
    for catdir in sorted(MP_CAT.iterdir()):
        if not catdir.is_dir(): continue
        for comp in sorted(catdir.iterdir()):
            if (comp / "SKILL.md").exists():
                assets.append(dict(id=f"mp:{catdir.name}/{comp.name}", type="skill",
                    source="mp", category=catdir.name, name=comp.name, path=comp))
    for typedir_name in ("skills", "agents", "commands", "mcps"):
        typedir = ECC_CAT / typedir_name
        if not typedir.exists(): continue
        for catdir in sorted(typedir.iterdir()):
            if not catdir.is_dir(): continue
            if typedir_name == "skills":
                for comp in sorted(catdir.iterdir()):
                    if (comp / "SKILL.md").exists():
                        assets.append(dict(id=f"ecc:skills/{catdir.name}/{comp.name}",
                            type="skill", source="ecc", category=catdir.name,
                            name=comp.name, path=comp))
            else:
                for f in sorted(catdir.iterdir()):
                    if f.is_file() and f.suffix in (".md", ".json"):
                        assets.append(dict(id=f"ecc:{typedir_name}/{catdir.name}/{f.stem}",
                            type={"agents": "agent", "commands": "command",
                                  "mcps": "mcp"}[typedir_name],
                            source="ecc", category=catdir.name, name=f.stem, path=f))
    return assets

def filter_assets(assets, source, types, components, only_core):
    core = [a for a in assets if a["source"] == "mp" and a["category"] not in ("in-progress", "misc", "deprecated")]
    if components:
        pats = [c.lower() for c in components]
        extras = [a for a in assets if any(
            p == "*" or a["id"].lower() == p or
            (p.endswith("*") and a["id"].lower().startswith(p[:-1])) or a["name"].lower() == p
            for p in pats)]
    else:
        extras = []
    if only_core:
        seen = set()
        out = []
        for a in core + extras:
            if a["id"] not in seen:
                seen.add(a["id"]); out.append(a)
        return out
    if source or types or components:
        assets = extras if components else assets
        if source: assets = [a for a in assets if a["source"] == source]
        if types:  assets = [a for a in assets if a["type"] in types]
    return assets

def discover_mp_bridge():
    return [dict(id="pack:mp-trellis-bridge", type="skill", source="pack",
                 category="bridge", name="mp-trellis-bridge",
                 path=ROOT / "skills" / "mp-trellis-bridge")]

# ---------- converters ----------

TOOLMAP_OPENCODE = {"read": "read", "glob": "read", "grep": "read", "ls": "read",
    "webfetch": "read", "websearch": "read", "write": "write", "edit": "write",
    "multiedit": "write", "notebookedit": "write", "bash": "bash", "task": "task",
    "todowrite": "write", "skill": "task"}

def agent_convert(fm, body, fmt, name):
    tools = [t.strip() for t in str(fm.get("tools", "")).split(",") if t.strip()]
    desc = str(fm.get("description", "")).strip()
    if fmt in (MD, MD_AGENT):
        return body_file(fm, body), None
    if fmt == MD_ZCODE:
        kept = {k: fm[k] for k in ("name", "description", "color") if k in fm}
        return body_file(kept, body), None
    if fmt == MD_PERMISSION:
        perm = sorted({TOOLMAP_OPENCODE.get(t.lower().split("(")[0], t.lower())
                       for t in tools} or {"read", "write", "bash"})
        perm_block = "\n".join(f"  {p}: allow" for p in perm)
        return body_file({"name": name, "description": fm.get("description", "")}, body,
                         extra="permission:\n" + perm_block), None
    if fmt == TOML:
        instr = body.replace('"""', '\\"\\"\\"')
        return None, f'name = "{q(name)}"\ndescription = "{q(desc[:300])}"\nsandbox_mode = "workspace-write"\ndeveloper_instructions = """\n{instr}\n"""\n'
    if fmt == JSON:
        return None, json.dumps({"name": name, "description": desc[:500],
            "tools": [t.lower() for t in tools], "instructions": body.strip()}, indent=2, ensure_ascii=False)
    raise ValueError(fmt)

def command_convert(fm, body, style, name):
    desc = str(fm.get("description", f"ECC command: {name}"))
    rel, content = None, None
    if style == CMD_MD_NS:
        rel = f"{NAMESPACE}/{name}.md"; content = body_file(fm, body)
    elif style == CMD_MD_FLAT:
        rel = f"{NAMESPACE}-{name}.md"; content = body_file(fm, body)
    elif style == CMD_WORKFLOW:
        rel = f"{NAMESPACE}-{name}.md"; content = body_file({"description": desc}, body)
    elif style == CMD_PROMPT:
        rel = f"{NAMESPACE}-{name}.prompt.md"; content = body_file(fm, body)
    elif style == CMD_TOML_NS:
        rel = f"{NAMESPACE}/{name}.toml"
        content = f'description = "{q(desc)}"\nprompt = """\n{body.replace(chr(34)*3, chr(92)+chr(34)*3)}\n"""\n'
    elif style == CMD_SKILL:
        rel = f"{NAMESPACE}-{name}/SKILL.md"
        content = body_file({"name": f"{NAMESPACE}-{name}", "description": desc,
            "disable-model-invocation": "true"}, body)
    return rel, content

def body_file(fm, body, extra=""):
    lines = ["---"]
    for k, v in fm.items():
        v = str(v)
        if "\n" in v:
            lines.append(f"{k}: |"); lines += [f"  {l}" for l in v.split("\n")]
        else:
            lines.append(f'{k}: "{v.replace(chr(34), chr(92)+chr(34))}"' if '"' in v else f"{k}: {v}")
    if extra:
        lines.append(extra)
    lines.append("---")
    return "\n".join(lines) + "\n" + body.lstrip("\n")

def mcp_merge(mcp_file: Path, snippet: dict, style):
    if style == MCP_TOML:
        blocks = []
        for name, cfg in snippet.get("mcpServers", snippet).items():
            b = [f'[mcp_servers.{name}]']
            if "command" in cfg: b.append(f'command = "{q(cfg["command"])}"')
            if "args" in cfg:    b.append("args = [" + ", ".join(f'"{q(a)}"' for a in cfg["args"]) + "]")
            if "env" in cfg:
                b.append(f"[mcp_servers.{name}.env]")
                b += [f'{k} = "{q(v)}"' for k, v in cfg["env"].items()]
            blocks.append("\n".join(b))
        return "\n\n".join(blocks) + "\n", "append"   # emit as separate snippet file
    existing = {}
    if mcp_file.exists():
        try: existing = json.loads(mcp_file.read_text(encoding="utf-8"))
        except Exception: existing = {}
    existing.setdefault("mcpServers", {}).update(snippet.get("mcpServers", snippet))
    return json.dumps(existing, indent=2, ensure_ascii=False) + "\n", "write"

# ---------- materialize ----------

def materialize(assets, platform_key, target, dry):
    p = PLATFORMS[platform_key]
    plan = []   # (rel_path, mode, content_or_srcdir)
    for a in assets:
        t = a["type"]
        if t == "skill":
            plan.append((f'{p["skills"]}/{a["name"]}', "dir", a["path"]))
        elif t == "agent":
            if p["agents"] is None: continue
            adir, fmt = p["agents"]
            fm, body = parse_frontmatter(a["path"].read_text(encoding="utf-8"))
            fm.setdefault("name", a["name"])
            c_or_txt, toml_or_json = agent_convert(fm, body, fmt, a["name"])
            if fmt == MD_AGENT:
                plan.append((f"{adir}/{a['name']}.agent.md", "write", c_or_txt))
            elif fmt in (MD, MD_ZCODE, MD_PERMISSION):
                plan.append((f"{adir}/{a['name']}.md", "write", c_or_txt))
            elif fmt == TOML:
                plan.append((f"{adir}/{a['name']}.toml", "write", toml_or_json))
            elif fmt == JSON:
                plan.append((f"{adir}/{a['name']}.json", "write", toml_or_json))
        elif t == "command":
            cdir, style = p["commands"]
            fm, body = parse_frontmatter(a["path"].read_text(encoding="utf-8"))
            if style == CMD_SKILL:
                rel, content = command_convert(fm, body, style, a["name"])
                plan.append((f'{p["skills"]}/{rel}', "write", content))
            else:
                rel, content = command_convert(fm, body, style, a["name"])
                plan.append((f"{cdir}/{rel}", "write", content))
        elif t == "mcp":
            mfile, style = p["mcp"]
            try:
                snippet = json.loads(a["path"].read_text(encoding="utf-8"))
            except Exception:
                continue
            if style == MCP_TOML:
                out, mode = mcp_merge(None, snippet, style)
                plan.append((f".codex/mcp-{a['name']}.toml", "write",
                    "# merge into .codex/config.toml\n" + out))
            else:
                plan.append((mfile, "mcp-merge", snippet))
    applied = merged = 0
    for rel, mode, payload in plan:
        dest = target / rel
        if dry:
            print(f"  [dry] {mode:9} {rel}"); applied += 1; continue
        if mode == "dir":
            shutil.copytree(payload, dest, dirs_exist_ok=True); applied += 1
        elif mode == "mcp-merge":
            dest.parent.mkdir(parents=True, exist_ok=True)
            out, _ = mcp_merge(dest, payload, MCP_JSON)
            dest.write_text(out, encoding="utf-8"); merged += 1
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(payload, encoding="utf-8"); applied += 1
    return applied, merged

# ---------- cli ----------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--platform", choices=sorted(PLATFORMS))
    ap.add_argument("--target", type=Path, default=Path.cwd())
    ap.add_argument("--type", dest="types", nargs="*", choices=["skill", "agent", "command", "mcp"])
    ap.add_argument("--source", choices=["mp", "ecc"])
    ap.add_argument("--component", nargs="*", help="ids or names, e.g. 'ecc:security/*' or 'tdd'")
    ap.add_argument("--only-core", action="store_true", help="just bridge + mattpocock main skills")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    assets = discover() + ([] if not args.only_core else discover_mp_bridge())
    if args.list:
        from collections import Counter
        by = Counter(f'{a["source"]}/{a["type"]}' for a in assets)
        for k, v in sorted(by.items()): print(f"{k:22} {v}")
        print(f"{'total':22} {sum(by.values())}")
        if args.platform:
            p = PLATFORMS[args.platform]
            print(f"\n{args.platform}: skills→{p['skills']}  agents→{p['agents']}  commands→{p['commands']}  mcp→{p['mcp']}  verified={p.get('verified')}")
        return
    if not args.platform:
        ap.error("--platform required (or --list)")
    selected = filter_assets(assets, args.source, args.types, args.component, args.only_core)
    if not selected:
        print("nothing selected"); return
    print(f"{len(selected)} assets → {args.platform} @ {args.target}")
    applied, merged = materialize(selected, args.platform, args.target.resolve(), args.dry_run)
    print(f"done: {applied} written, {merged} mcp-merge(s)")

if __name__ == "__main__":
    main()
