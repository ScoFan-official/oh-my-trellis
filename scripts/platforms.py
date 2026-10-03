"""Per-platform file locations for skills / sub-agents / commands / MCP config.

Single source of truth shared by build_manifest.py and install.py.

Source: docs.trytrellis.app/beta — custom-skills, custom-agents, custom-commands,
plus real generated files from mindfold-ai/Trellis templates.

- agents=None: platform has no sub-agent primitive (work runs inline).
- commands="skill": platform has no command primitive; commands ship as
  user-invoked skills under that platform's skills_dir.
- verified=False: convention-based guess (CC-style md, `.X/agents`,
  `.X/commands`); documented but not yet observed in the wild.
"""

# agent formats
MD = "md"                      # Claude-style md w/ tools: — passthrough
MD_AGENT = "md-agent"          # Copilot: {name}.agent.md
MD_PERMISSION = "md-permission"  # OpenCode: permission: object
MD_ZCODE = "md-zcode"          # ZCode: name/description/color, no tools:
TOML = "toml"                  # Codex: developer_instructions
JSON = "json"                  # Kiro: {"tools": [...], ...}

# command styles
CMD_MD_NS = "md-ns"            # <dir>/<ns>/<name>.md
CMD_MD_FLAT = "md-flat"        # <dir>/<ns>-<name>.md
CMD_TOML_NS = "toml-ns"        # Gemini: <dir>/<ns>/<name>.toml, prompt="""..."""
CMD_PROMPT = "prompt"          # Copilot: <dir>/<ns>-<name>.prompt.md
CMD_WORKFLOW = "workflow"      # <dir>/<ns>-<name>.md (workflow-file platforms)
CMD_SKILL = "skill"            # commands ship as SKILL.md under skills_dir

# mcp styles
MCP_JSON = "mcp-json"          # {"mcpServers": {...}} file
MCP_TOML = "mcp-toml"          # Codex [mcp_servers.*] in config.toml

PLATFORMS = {
    # key: (skills_dir, agents, commands, mcp, verified, notes)
    "claude":      dict(skills=".claude/skills",      agents=(".claude/agents", MD),            commands=(".claude/commands", CMD_MD_NS),    mcp=(".mcp.json", MCP_JSON),              verified=True),
    "cursor":      dict(skills=".cursor/skills",      agents=(".cursor/agents", MD),            commands=(".cursor/commands", CMD_MD_FLAT),  mcp=(".cursor/mcp.json", MCP_JSON),        verified=True),
    "opencode":    dict(skills=".opencode/skills",    agents=(".opencode/agents", MD_PERMISSION), commands=(".opencode/commands", CMD_MD_NS), mcp=("opencode.json", MCP_JSON),          verified=True),
    "codex":       dict(skills=".agents/skills",      agents=(".codex/agents", TOML),           commands=(None, CMD_SKILL),                  mcp=(".codex/config.toml", MCP_TOML),      verified=True),
    "kiro":        dict(skills=".kiro/skills",        agents=(".kiro/agents", JSON),            commands=(None, CMD_SKILL),                  mcp=(".kiro/settings/mcp.json", MCP_JSON), verified=True),
    "gemini":      dict(skills=".agents/skills",      agents=(".gemini/agents", MD),            commands=(".gemini/commands", CMD_TOML_NS),  mcp=(".gemini/settings.json", MCP_JSON),   verified=True),
    "qoder":       dict(skills=".qoder/skills",       agents=(".qoder/agents", MD),             commands=(".qoder/commands", CMD_MD_FLAT),   mcp=(".qoder/mcp.json", MCP_JSON),         verified=True),
    "codebuddy":   dict(skills=".codebuddy/skills",   agents=(".codebuddy/agents", MD),         commands=(".codebuddy/commands", CMD_MD_NS), mcp=("mcp.json", MCP_JSON),              verified=True),
    "copilot":     dict(skills=".github/skills",      agents=(".github/agents", MD_AGENT),      commands=(".github/prompts", CMD_PROMPT),    mcp=(".vscode/mcp.json", MCP_JSON),       verified=True),
    "droid":       dict(skills=".factory/skills",     agents=(".factory/droids", MD),           commands=(".factory/commands", CMD_MD_NS),   mcp=(".factory/mcp.json", MCP_JSON),      verified=True),
    "pi":          dict(skills=".agents/skills",      agents=(".pi/agents", MD),                commands=(".pi/prompts", CMD_MD_FLAT),       mcp=(".pi/mcp.json", MCP_JSON),           verified=True),
    "omp":         dict(skills=".omp/skills",         agents=(".omp/agents", MD),               commands=(".omp/commands", CMD_MD_FLAT),     mcp=(".omp/mcp.json", MCP_JSON),          verified=False),
    "kilo":        dict(skills=".kilocode/skills",    agents=None,                              commands=(".kilocode/workflows", CMD_WORKFLOW), mcp=(".kilocode/mcp.json", MCP_JSON),    verified=True),
    "antigravity": dict(skills=".agent/skills",       agents=None,                              commands=(".agent/workflows", CMD_WORKFLOW), mcp=(".agent/mcp.json", MCP_JSON),        verified=False),
    "devin":       dict(skills=".devin/skills",       agents=None,                              commands=(".devin/workflows", CMD_WORKFLOW), mcp=(".devin/mcp.json", MCP_JSON),         verified=True,  notes="No sub-agent primitive; commands = .devin/workflows/{ns}-{name}.md. MCP config per Devin CLI docs."),
    "reasonix":    dict(skills=".reasonix/skills",    agents=(".reasonix/agents", MD),          commands=(".reasonix/commands", CMD_MD_FLAT), mcp=(".reasonix/mcp.json", MCP_JSON),    verified=False),
    "zcode":       dict(skills=".zcode/skills",       agents=(".zcode/agents", MD_ZCODE),       commands=(".zcode/commands", CMD_MD_FLAT),   mcp=(".zcode/mcp.json", MCP_JSON),        verified=False, notes="agents format verified against Trellis zcode template; commands/MCP guessed by convention."),
    "trae":        dict(skills=".trae/skills",        agents=(".trae/agents", MD),              commands=(".trae/commands", CMD_MD_FLAT),    mcp=(".trae/mcp.json", MCP_JSON),         verified=False),
    "grok":        dict(skills=".grok/skills",        agents=(".grok/agents", MD),              commands=(".grok/commands", CMD_MD_FLAT),    mcp=(".grok/mcp.json", MCP_JSON),         verified=False),
    "kimi":        dict(skills=".kimi-code/skills",   agents=(".kimi-code/agents", MD),         commands=(".kimi-code/commands", CMD_MD_FLAT), mcp=(".kimi-code/mcp.json", MCP_JSON),  verified=False),
    "snow":        dict(skills=".snow/skills",        agents=(".snow/agents", MD),              commands=(".snow/commands", CMD_MD_FLAT),    mcp=(".snow/mcp.json", MCP_JSON),         verified=False),
    "dsh":         dict(skills=".dsh/skills",         agents=(".dsh/agents", MD),               commands=(".dsh/commands", CMD_MD_FLAT),     mcp=(".dsh/mcp.json", MCP_JSON),          verified=False, notes="DeepSeek Harness; native continuable subagents, least-documented platform."),
}
