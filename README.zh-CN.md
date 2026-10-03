# mp-trellis-pack

[English](./README.md) · **简体中文**

一个公共的**资产包 + 分发枢纽**：把三个生态——
[mattpocock/skills](https://github.com/mattpocock/skills)、
[Everything Claude Code](https://github.com/davila7/claude-code-templates)（ECC）、
[Trellis](https://github.com/mindfold-ai/Trellis)——融合进同一个仓库，
并落到 **22 个 agent 平台**的原生格式。

## 资产清单（1,740+）

| 层 | 内容 | 分发方式 |
| --- | --- | --- |
| `marketplace/` | Trellis spec-registry 模板（`agent-workflow`）——mp 技能的 Trellis 后端合约 | `trellis init --registry` |
| `skills/` | **38 个技能**：`mp-trellis-bridge` + mattpocock 全量（engineering 19 / productivity 7 / misc 4 / in-progress 6 +1） | `npx skills add` |
| `catalog/` | 全量镜像：**mp docs + claude-plugin + .agents**，ECC 完整组件——**889 skills / 422 agents / 288 commands / 104 MCPs**，以及 hooks/loops/mods/settings/sandbox | `scripts/install.py` |

## 三条安装通道

### 1. Trellis spec registry —— 合约层

```bash
trellis init --registry gh:ScoFan-official/mp-trellis-pack/marketplace --template agent-workflow --append
```

向 `.trellis/spec/` 安装 `agents/` + `guides/` 规范文件，带 `paths:` 作用域注入：
tracker 合约（spec → 任务目录、ticket → 子任务、triage → `meta.triage`、
wayfinder → `map.md`）、triage 角色表、domain 文档约定、mp×Trellis 集成指南。

### 2. skills CLI —— 核心技能集

```bash
npx skills add ScoFan-official/mp-trellis-pack --agent <platform> --copy
```

对任意受支持平台（`devin`、`codex`、`claude`…）安装全部 38 个技能。
`mp-trellis-bridge` 首次加载时自动播种 spec 合约。

### 3. install.py —— 全量目录，按平台落地

```bash
# 资产盘点
python scripts/install.py --list

# 全量安装到指定平台（ECC + mp 全部）
python scripts/install.py --platform codex --target /path/to/repo
python scripts/install.py --platform devin --target /path/to/repo
python scripts/install.py --platform zcode --target /path/to/repo

# 精确安装
python install.py --platform codex --target . \
  --component "ecc:agents/security/*" "ecc:commands/git-workflow/commit" "mp:engineering/tdd"

# 只装推荐核心（bridge + mp 主技能）
python install.py --platform zcode --target . --only-core

# 预览不写入
python install.py --platform claude --target . --dry-run
```

## 平台支持（22 个）

每种资产都落到该平台的原生位置和格式：

| 平台 | skills | sub-agents | commands | mcp |
| --- | --- | --- | --- | --- |
| claude / cursor / codebuddy / droid / qoder / pi / gemini | 原生目录 | md | md commands | json |
| opencode | `.opencode/skills` | md + `permission:` | md | json |
| **codex** | `.agents/skills` | **`.toml` + `developer_instructions`** | 包装为技能 | `config.toml` 片段 |
| kiro | `.kiro/skills` | json | 包装为技能 | json |
| copilot | `.github/skills` | `*.agent.md` | `*.prompt.md` | json |
| **devin** | `.devin/skills` | —（inline 运行） | `.devin/workflows/` | json |
| **zcode** | `.zcode/skills` | md（剥离 `tools:`） | md | json |
| kilo / antigravity | 原生目录 | —（inline 运行） | workflows | json |
| omp / reasonix / trae / grok / kimi / snow / dsh | 原生目录 | md（约定推断） | md（约定推断） | json |

`verified` 平台按 Trellis 官方文档的文件位置生成；其余平台为约定推断
（在 `scripts/platforms.py` 和 `manifest.json` 中标注）——其 agent/command
产物视为待人工复核的草稿。

## 仓库结构

```
marketplace/            # Trellis spec registry（index.json + agent-workflow 模板）
skills/                 # npx-skills 安装面：bridge + mp 全量技能
catalog/
├── manifest.json       # 每个资产 → 各平台目标路径
├── upstream.json       # 上游 pin 住的 commit SHA
├── ATTRIBUTION.md
├── mattpocock/         # skills(4 类) + docs + .claude-plugin + .agents
└── ecc/                # skills agents commands hooks mcps loops mods settings sandbox
scripts/
├── platforms.py        # 22 平台位置表（单一真源）
├── install.py          # catalog → 任意平台、任意子集
├── build_manifest.py   # 重新生成 manifest.json
└── sync_upstream.py    # 重新 vendor 上游（--check = 只看漂移）
```

## 未移植的部分（有意为之）

ECC 的 `hooks/`、`settings/`、`loops/`、`mods/`、`sandbox/` 保留在 `catalog/`
中作参考——它们是 Claude Code 私有格式（hook JSON、settings.json、sandboxed
bash），移植等于逐平台重写。mp 的 `.claude-plugin/` 原样保留，Claude 用户
可直接挂他的原生 marketplace。

## 更新方式

```bash
python scripts/sync_upstream.py --check   # 查看上游是否有更新
python scripts/sync_upstream.py           # 重新 vendor catalog/
python scripts/build_manifest.py          # 刷新 manifest
npx skills update                          # 使用侧更新已装技能
```

已安装的 spec 归项目所有（Trellis 模型）；`catalog/` 是本包的 vendor 副本——
不要在原地改，sync 会覆盖。

## 依赖

- Python 3.8+、git、通道 2 需要 `npx skills`
- 通道 1（spec registry）仅在 Trellis 管理的仓库中有意义
