<p align="center">
  <img src="assets/hero.png" alt="oh-my-trellis — mattpocock × ECC × impeccable，一条 Trellis 主轴">
</p>

<p align="center">
  <strong>有工作流脊梁的 agent 技能包。</strong>
</p>

<p align="center">
  <a href="https://github.com/ScoFan-official/oh-my-trellis/stargazers"><img src="https://img.shields.io/github/stars/ScoFan-official/oh-my-trellis?style=flat&colorA=222222&colorB=CB3837" alt="Stars"></a>
  <img src="https://img.shields.io/badge/catalog-1%2C741%20assets-3FB950?style=flat&colorA=222222" alt="1,741 catalog assets">
  <img src="https://img.shields.io/badge/platforms-22-58A6FF?style=flat&colorA=222222" alt="22 agent platforms">
  <img src="https://img.shields.io/badge/upstreams-3-E05735?style=flat&colorA=222222" alt="3 vendored upstreams">
  <a href="https://github.com/ScoFan-official/oh-my-trellis/commits"><img src="https://img.shields.io/github/last-commit/ScoFan-official/oh-my-trellis?style=flat&colorA=222222" alt="Last commit"></a>
</p>

<p align="center">
  <a href="./README.md">English</a> · <strong>简体中文</strong> · vendored 遵循 MIT &amp; Apache-2.0 —— 见 <a href="catalog/ATTRIBUTION.md">ATTRIBUTION</a>
</p>

advisory 技能运不出设计系统——合约可以。oh-my-trellis 把
[mattpocock/skills](https://github.com/mattpocock/skills)、
[Everything Claude Code](https://github.com/davila7/claude-code-templates) 和
[pbakaus/impeccable](https://github.com/pbakaus/impeccable) vendor 进同一个仓库，
再把它们嘴里的抽象名词——"the issue tracker"、"PRODUCT.md"、"DESIGN.md"——
绑进 Trellis 的 `.trellis/` 主轴，把工作流从"建议执行"变成"强制执行"。

**3** 个 vendored 上游 · **1,741** 个目录资产 · **41** 个默认技能 · **22** 个平台 · **1** 层合约——对 vendored 文件零 patch。

---

## 安装

| 你想要… | 运行 |
| --- | --- |
| 只要 Trellis 合约规范 | `trellis init --registry gh:ScoFan-official/oh-my-trellis/marketplace --template agent-workflow --append` |
| 推荐技能集（mp 全量 37 个 + impeccable + 本包自建 `mp-trellis-bridge` / `oh-my-update` / `trellis-domains`） | `npx skills add ScoFan-official/oh-my-trellis --agent <platform> --copy` |
| 1741 资产目录库里的任何东西 | `python scripts/install.py --platform <platform> --target <repo>` |

仓库已公开，三条通道均无需认证，可自由组合。

### 一句话安装提示词（直接发给 agent）

把下面这段贴给 Devin / Codex / ZCode / Claude / Cursor，它会自己完成全部初始化：

> 在本仓库安装 Trellis 和 oh-my-trellis：① 装我们的 Trellis CLI 并初始化——`npm i -g https://github.com/ScoFan-official/oh-my-trellis/releases/download/cli-v0.6.17-ohmy.2/oh-my-trellis-0.6.17-ohmy.2.tgz`（若已全局安装 `@mindfoldhq/trellis` 需先 `npm rm -g @mindfoldhq/trellis`——本包占用 `trellis` bin），然后 `trellis init --devin`——registry 与默认 workflow 已内嵌在 fork 里；② 跑 `trellis init --template agent-workflow --append` 安装 spec 合约；③ 给你的平台装技能——优先 `npx skills add ScoFan-official/oh-my-trellis --agent <你的平台> --copy`；若你的平台不被覆盖，改用 `git clone --depth 1 https://github.com/ScoFan-official/oh-my-trellis /tmp/mtp && python /tmp/mtp/scripts/install.py --platform <你的平台> --target . --only-core`；④ 调用 `mp-trellis-bridge` 技能完成 `AGENTS.md` 播种，然后读 `.trellis/spec/agents/issue-tracker.md`，向我汇报你对 spec、ticket、triage、实现分别会用哪些 tracker 动词。之后要更新，调用 `oh-my-update` 技能。

非 Trellis 仓库、只要技能时用这个短版：

> 在本仓库安装 mattpocock 技能集：`npx skills add ScoFan-official/oh-my-trellis --agent <你的平台> --copy`；装好后浏览 https://github.com/ScoFan-official/oh-my-trellis 的 `catalog/INDEX.md`，如需更多组件用 `scripts/install.py` 按本机平台补装。

---

## 01 · 合约 —— Trellis spec registry

技能说 "publish to the issue tracker"，指向 `.trellis/tasks/`；
说 "更新 PRODUCT.md / DESIGN.md"，指向 `.trellis/spec/`。
`paths:` frontmatter 按路径作用域注入——每份合约恰好在 agent 触碰它管的文件时加载。
前端闸门同理：碰 `*.tsx` 就收到 `frontend-craft.md`；
`implement.md` 没有 `## Design review` 小节，不算 READY。

```bash
trellis init --registry gh:ScoFan-official/oh-my-trellis/marketplace --template agent-workflow --append
```

安装到 `.trellis/spec/`：

```
.trellis/spec/
├── agents/
│   ├── index.md
│   ├── issue-tracker.md      # 核心合约——agent 触碰 .trellis/tasks/ 或 .scratch/ 时自动注入
│   ├── triage-labels.md      # 五角色 → meta.triage / Status: 行——inbox/任务操作时注入
│   ├── frontend-craft.md     # impeccable 绑定 + Design review 闸门——触碰前端文件时注入
│   └── domain.md             # GLOSSARY.md + docs/adr/ 约定——编辑 domain 文档时注入
└── guides/
    └── mp-integration.md     # 阶段映射、泳道规则、技能优先级（拉取式文档）
```

所有文件带 `paths:` frontmatter，Trellis dynamic spec loading 在 agent
触碰对应文件时自动注入该合约。`--append` 只补缺省文件，对已有 spec 树安全。
安装后文件归项目所有（Trellis 项目所有权模型），可自行修改。

## 02 · 技能集 —— skills CLI

```bash
npx skills add ScoFan-official/oh-my-trellis --agent <platform> --copy
```

安装 **41 个技能**——mattpocock 全集
（engineering / productivity / misc / in-progress）+ `impeccable` 前端设计工作流
+ 本包自建 `mp-trellis-bridge`、`oh-my-update`、`trellis-domains`。
`--agent` 支持 `devin`、`codex`、`claude`、`cursor` 等 skills CLI 识别的平台。

`mp-trellis-bridge` 是自举器 + 路由合约：首次加载时验证 `.trellis/`、
安装通道 1 的 spec 合约（registry 优先、内置模板兜底）、向 `AGENTS.md`
幂等追加 `## Agent skills` 块、检查 mp 技能是否就位。之后是 no-op。

## 03 · 目录库 —— install.py

`scripts/install.py` 把目录库中任意子集物化到目标仓库，
并转换成该平台的原生格式。

```bash
# 盘点
python scripts/install.py --list
python scripts/install.py --list --platform codex      # 附带落地位置

# 全量装某个平台
python scripts/install.py --platform codex --target /path/to/repo
python scripts/install.py --platform devin --target /path/to/repo
python scripts/install.py --platform zcode --target /path/to/repo

# 只装推荐核心（bridge + mp 主技能，不含 in-progress/misc）
python scripts/install.py --platform zcode --target . --only-core

# 精确挑选——按 id、名称或 glob
python scripts/install.py --platform claude --target . \
  --component "ecc:agents/security/*" "ecc:commands/git-workflow/commit" "mp:engineering/tdd"

# 按类型或来源过滤
python scripts/install.py --platform cursor --target . --type skill agent
python scripts/install.py --platform copilot --target . --source mp

# 预览
python scripts/install.py --platform devin --target . --dry-run
```

参数：`--platform`（必填）、`--target`（仓库根，默认 `.`）、
`--type skill|agent|command|mcp`、`--source mp|ecc`、
`--component <id|名称|glob>`、`--only-core`、`--dry-run`、`--list`。

**资产 ID** 形如 `来源:类型-路径`：`mp:engineering/tdd`、
`ecc:skills/development/api-design-principles`、
`ecc:agents/security/security-auditor`、`ecc:commands/git-workflow/commit`、
`ecc:mcps/database/dbhub`。完整 ID 见 `catalog/manifest.json`。

### 每类资产落到哪（按平台）

- **skills** → `<平台技能目录>/<name>/`——文件夹直拷（跨平台通用格式）
- **agents** → 平台 sub-agent 文件 + 转换后的 frontmatter
- **commands** → 平台的 command/workflow/prompt 文件；无命令原语的平台
  包装为用户触发技能（`ecc-<name>/SKILL.md`，`disable-model-invocation`）
- **mcps** → 合并进平台 MCP JSON 配置；Codex 生成
  `.codex/mcp-<name>.toml` 片段供合入 `config.toml`

## 组件如何被触发

| 类型 | 触发模型 | 你说… |
| --- | --- | --- |
| skills（889） | **语义自动匹配**：平台把每个 SKILL.md 的 `name`+`description` 注入 agent 的可用技能清单，任务命中描述时自行加载（"出问题了"→`diagnosing-bugs`）；也可显式点名。 | "帮我查这个 bug" 或 "用 `api-design-principles`" |
| commands（288） | **显式触发**：有命令原语的平台走原生命令语法；没有的平台（codex/devin/kiro）包装为 `disable-model-invocation` 技能，按名调用。 | "/ecc-commit" 或 "跑 `ecc-commit`" |
| agents（422） | **分派触发**：走平台 sub-agent 机制（Claude 的 `Task`、Codex 子代理），描述命中自动分派或点名委派。**devin/kilo/antigravity 无此原语不安装**（manifest 标 n/a；可把 body 当 inline 角色提示用）。 | "让 `security-auditor` 复审这段" |
| mcps（104） | **配置激活**：合入平台 MCP 配置，重启握手后工具进工具箱。多数需要凭据——先填 `<your-...>` 占位符。 | 工具自动出现 |

**不要一次全装 889 个技能**——每个 name+description 都占系统提示位，全装会稀释匹配精度。推荐 `--only-core` 或 `--component` 按需选装；把 `catalog/INDEX.md` 当货架，用时再取。

## 平台支持（22 个）

| 平台 | skills 目录 | sub-agents | commands | mcp | 状态 |
| --- | --- | --- | --- | --- | --- |
| claude | `.claude/skills` | `.claude/agents/*.md` | `.claude/commands/ecc/*` | `.mcp.json` | ✅ 已验证 |
| cursor | `.cursor/skills` | `.cursor/agents/*.md` | `.cursor/commands/ecc-*` | `.cursor/mcp.json` | ✅ |
| opencode | `.opencode/skills` | `.opencode/agents/*.md`（+`permission:`） | `.opencode/commands/ecc/*` | `opencode.json` | ✅ |
| **codex** | `.agents/skills` | `.codex/agents/*.toml`（`developer_instructions`） | → 技能包装 | `.codex/mcp-*.toml` | ✅ |
| kiro | `.kiro/skills` | `.kiro/agents/*.json` | → 技能包装 | `.kiro/settings/mcp.json` | ✅ |
| gemini | `.agents/skills` | `.gemini/agents/*.md` | `.gemini/commands/ecc/*.toml` | `.gemini/settings.json` | ✅ |
| qoder | `.qoder/skills` | `.qoder/agents/*.md` | `.qoder/commands/ecc-*` | `.qoder/mcp.json` | ✅ |
| codebuddy | `.codebuddy/skills` | `.codebuddy/agents/*.md` | `.codebuddy/commands/ecc/*` | `mcp.json` | ✅ |
| copilot | `.github/skills` | `.github/agents/*.agent.md` | `.github/prompts/*.prompt.md` | `.vscode/mcp.json` | ✅ |
| droid | `.factory/skills` | `.factory/droids/*.md` | `.factory/commands/ecc/*` | `.factory/mcp.json` | ✅ |
| pi | `.agents/skills` | `.pi/agents/*.md` | `.pi/prompts/ecc-*` | `.pi/mcp.json` | ✅ |
| **devin** | `.devin/skills` | —（无原语，inline） | `.devin/workflows/ecc-*.md` | `.devin/mcp.json` | ✅ |
| kilo | `.kilocode/skills` | —（inline） | `.kilocode/workflows/ecc-*` | `.kilocode/mcp.json` | ✅ |
| **zcode** | `.zcode/skills` | `.zcode/agents/*.md`（无 `tools:`） | `.zcode/commands/ecc-*` | `.zcode/mcp.json` | ⚠️ 部分验证 |
| omp / reasonix / trae / grok / kimi / snow / dsh / antigravity | 各自 `.X/skills` | `.X/agents/*.md`（约定） | `.X/commands|workflows/ecc-*` | `.X/mcp.json` | ⚠️ 约定推断 |

✅ = 文件位置遵循 Trellis 官方 per-platform 文档表。
⚠️ = 约定推断（`scripts/platforms.py` / `manifest.json` 中标
`verified: false`）——生成的 agent/command 文件视为待复核草稿。
`zcode` 的 agents 格式已对照 Trellis 官方 zcode 模板验证；
commands/MCP 路径为约定推断。

---

## 资产目录明细

**每个组件的"何时使用"**：见 [`catalog/INDEX.md`](catalog/INDEX.md)——
自动生成的索引，1,741 个组件每个都带自己的 description
（"use when…"），抽取自源文件 frontmatter。
重新生成：`python scripts/build_index.py`。

### mattpocock 技能 —— 37 个（+ 本包自建）

本包的工程主干。主线流程：*grill → spec → tickets → implement → retro*，
外加两条入口匝道和独立工具。

| 技能 | 何时使用 |
| --- | --- |
| `ask-matt` | 路由器——"我这个情况该用哪个技能？"不确定时先问它。 |
| `grill-with-docs` | 对齐想法：agent 按设计树连续追问你，术语落 `GLOSSARY.md`、决策落 `docs/adr/`。仓库内一律用它（优于 `grill-me`）。 |
| `grill-me` / `grilling` | 同款追问但无文档副作用（无工作目录时用）；`grilling` 是引擎，`grill-me` 是用户入口。 |
| `to-spec` | 把 grill 完的对话固化成 spec（Problem/Solution/User Stories/Decisions）→ Trellis 任务 + `prd.md`。 |
| `to-tickets` | 把 spec 纵切成 tracer-bullet 工单 → 子任务 + `blocked_by` meta，写入前先确认拆法。 |
| `implement` | 实现一张工单：预约定接缝内 TDD 红绿 → 类型检查/测试 → code-review → 提交。一张工单一个会话。 |
| `implement-spec` | 批量编排整个 spec 的工单图（integration 分支 + 并行 worktree）。Devin 下顺序执行或手动 `run_subagent`。 |
| `tdd` | 红-绿-重构循环，嵌在 `implement` 内部用。 |
| `code-review` | 双轴评审（Standards + Spec）ref 以来的改动，与 `trellis-check` 互补。 |
| `codebase-design` | 深模块词汇表（interface/depth/seam/deletion test），设计讨论用。 |
| `improve-codebase-architecture` | 扫描浅模块 → HTML 可视化报告 → 挑一个 grill 细化。成长期代码库建议隔几天跑一次。 |
| `diagnosing-bugs` | 硬 bug/性能回退：先建必红复现回路，再假设-插桩-修复-回归。 |
| `domain-modeling` | 建/磨 `GLOSSARY.md` + ADR；在 grill/wayfinder 内部惰性触发。 |
| `research` | 把问题派给高信源做调研 → 落 markdown 发现文件。 |
| `prototype` | 一次性原型验证设计问题（grill↔prototype 往返）。 |
| `triage` | 分诊外部报单：`needs-triage→needs-info/ready-for-agent/ready-for-human/wontfix`；`.scratch/` 收件、升格为任务。 |
| `wayfinder` | 迷雾级工程：父任务 + `map.md` + 决策工单（research/prototype/grilling/task），每会话最多 resolve 一张。 |
| `retro` | 构建后环境调优：导航指针、确定性检查、评审清单。 |
| `handoff` | 压缩会话 → 交接文档给下一个 agent/会话；自动脱敏。 |
| `teach` | 把目录变成多会话教学 workspace（使命→资源→课程→记录）。 |
| `to-questionnaire` | 把卡住你的决策变成发给真人的 markdown 问卷。 |
| `wait-what` | "没看懂，重讲"——简化技术英语 + 术语表重述。 |
| `writing-for-agents` | 撰写/编辑技能、AGENTS.md、CLAUDE.md。 |
| `pr` / `wizard` | 写 PR body；为只能人做的事（基础设施、控制台）生成交互式 bash 向导。 |
| `setup-matt-pocock-skills` | 面向非 Trellis 仓库的旧自举器——本包中由 `mp-trellis-bridge` 取代。 |
| `claude-handoff`、`loop-me`、`setup-ts-deep-modules`、`writing-beats`、`writing-fragments`、`writing-shape` | in-progress 合集——可用但打磨度低。 |
| `git-guardrails-claude-code`、`migrate-to-shoehorn`、`scaffold-exercises`、`setup-pre-commit` | misc——平台特定或小众。 |
| `mp-trellis-bridge` | **本包自建**。把以上全部绑定到 Trellis 的合约 + 路由器。 |
| `oh-my-update` | **本包自建**。确认门后的整栈更新——fork CLI、`.trellis/` 模板、已装技能、`.trellis/spec/` 合约——升到 ScoFan-official 最新 release。 |
| `trellis-domains` | **本包自建**。`.trellis/domains/` 板块层的薄壳——归口、插旗、接手读档链、worklog/收工、对账检查清单，逐条指回仓内 `DISCIPLINE.md` / `WORKLOG-PROTOCOL.md` / `REGISTRY.md`（协议正文不住这里）。 |

### impeccable —— 1 个技能，24 条命令（前端设计）

[pbakaus/impeccable](https://github.com/pbakaus/impeccable)，Apache-2.0——
前端精工工作流。本包只 vendor **markdown 层**：`/impeccable <cmd>` 技能
（`shape`、`craft`、`critique`、`audit`、`polish`、`bolder`、`typeset`…）
在所有平台可用；61 条确定性检测规则、`live`、`generate`、`hooks`、`doctor`
及 `impeccable context` 启动器需要上游引擎——在目标项目跑
`npx impeccable install`。没装引擎时命令走技能自带的 degraded 降级模式。

在 Trellis 仓库里，`agents/frontend-craft.md` 绑定 impeccable 的产物：
PRODUCT.md → `.trellis/spec/product.md`、DESIGN.md → `.trellis/spec/design-system.md`；
把 `shape → craft → audit+critique → polish` 接进各相位；并给前端任务上闸门——
`implement.md` 没有 `## Design review` 小节就不能记 READY。

### ECC（Everything Claude Code）—— 1,703 个组件

最大的社区 agent 组件目录库（aitmpl.com）。以下为 `install.py --list`
真实统计：

| 类型 | 数量 | 主要分类 | 说明 |
| --- | --- | --- | --- |
| skills | **889** | development 230、scientific 135、ai-research 131、productivity 50、business-marketing 48、security 47、creative-design 33、enterprise-communication 33、web-development 30、career 21… | SKILL.md 目录（含 references/scripts），拷到任意平台技能目录即可 |
| agents | **422** | expert-advisors 52、programming-languages 50、devops-infrastructure 40、data-ai 40、development-tools 35、security 25、business-marketing 21、development-team 18、deep-research-team 16、web-tools 16… | Claude md → 按平台转换 |
| commands | **288** | google-workspace 47、utilities 21、project-management 20、testing 17、svelte 16、orchestration 15、git-workflow 14、sync 14、team 14、deployment 11… | Claude 命令 → 转换/包装 |
| mcps | **104** | devtools 49、web-data 10、database 8、integration 8、browser_automation 6、web 6、productivity 5… | `mcpServers` JSON 片段 |

未移植（保留在 `catalog/` 作参考，Claude Code 私有格式）：
**hooks 81**、**settings 75**、**mods ~40**、**sandbox 23**（cloudflare/docker/e2b）、**loops 18**。

每个组件的使用场景：[`catalog/INDEX.md`](catalog/INDEX.md)。

## 仓库结构

```
marketplace/            # 通道 1：Trellis spec registry（index.json + agent-workflow）
skills/                 # 通道 2：npx-skills 安装面——本包自建技能 + mp 全量 37 技能 + impeccable
catalog/
├── INDEX.md            # 生成：每个组件 + 使用场景
├── manifest.json       # 生成：每个资产 → 各平台目标路径
├── upstream.json       # 上游 pin 的 SHA
├── ATTRIBUTION.md      # MIT 出处
├── mattpocock/         # skills(4 合集) + docs + .claude-plugin + .agents + LICENSE
├── impeccable/         # skills/impeccable + docs + LICENSE + NOTICE.md（Apache-2.0）
└── ecc/                # skills agents commands mcps hooks loops mods settings sandbox + LICENSE
scripts/
├── platforms.py        # 22 平台位置表（单一真源）
├── install.py          # 目录库 → 平台原生文件
├── build_manifest.py   # 重新生成 manifest.json
├── build_index.py      # 重新生成 INDEX.md
└── sync_upstream.py    # 重新 vendor 上游（--check = 漂移报告）
```

## 更新方式

使用侧：单一入口——**`/oh-my-update`** workflow（Devin）或 `oh-my-update`
技能（`skills/oh-my-update/`）。它检查 fork CLI 在本仓库 `cli-v*` release
下的最新版本（CLI tarball 通道与 pack `v*` release 同页共存）、刷新已装
技能并补装 spec 合约，动手前有确认闸门。分层兜底：
`npx skills add ScoFan-official/oh-my-trellis --agent <平台> --copy`。

本包维护侧（重新 vendor 上游）：

```bash
python scripts/sync_upstream.py --check   # 上游动了吗？
python scripts/sync_upstream.py           # 重新 vendor catalog/（只覆盖 catalog）
python scripts/build_manifest.py && python scripts/build_index.py
```

已安装 spec 归项目所有（Trellis 模型）——上游 spec 变更需人工合并。
`catalog/` 是 vendor 副本，不要在原地改。

## 依赖

- Python 3.8+、git
- `npx skills`（Node.js）用于通道 2
- Trellis 管理的仓库仅在通道 1（spec registry）需要
- Claude 私有格式扩展（hooks/settings 等）需 Claude Code 才能原样使用

## FAQ

**私有/分叉副本？** 仓库已公开，三条通道均无需认证。分叉可 pin 自己的
快照；把 `--registry` 改成 `gh:you/fork` 即可。

**我在哪个平台？** `install.py --list --platform X` 会打印该平台下
每类资产的落地位置，装之前先看。

**技能太多？** 通道 3 默认装你显式选择的子集；`--only-core` 给出
~28 个推荐技能。`npx skills add --skill <name>` 可从 `skills/` 单装。

**发现平台路径不对？** 改 `scripts/platforms.py`（单一真源），
然后重跑 `install.py` 和 `build_manifest.py`。
