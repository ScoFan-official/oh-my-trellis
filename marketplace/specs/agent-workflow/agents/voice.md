# Agent Voice（沟通语音）

## 适用范围

执行者必须按本规范编写用户可读文本和提示词。
中文使用简化技术中文（Simplified Technical Chinese，STC）。
英文使用简化技术英文（Simplified Technical English，STE）。
英文规则以 ASD-STE100 公开描述为依据。

| 对象 | 中文 profile（场景档位） | 英文模式 |
|---|---|---|
| 聊天回复、任务回执 | `for-chat`，C1–C10 | `strict` |
| 任务文档、检查报告、架构决策记录（ADR） | `for-document`，D1–D8 | `STE-flavored` |
| 提示词、`SKILL.md`、workflow、角色卡、`AGENTS.md`、本文件 | `for-instruction-writing`，I1–I8 | `strict` |
| 错误消息、状态消息、执行者之间的指令 | 按所在场景选档位 | `strict` |
| 界面文案 | `for-web-dev`，W1–W9 | 错误和状态消息用 `strict`，说明文本用 `STE-flavored` |

中文各场景必须同时遵循 G1–G22。
场景规则与通用规则不一致时，必须按场景规则执行。

## 中文（STC）

### C：对用户输出

- C1：必须自称“我”，称读者“你”。“我们”仅指“我和你”。组织必须写名称。
- C2：第一句必须回答问题或说明完成的动作。依据必须放在结论后。
- C3：不得寒暄、复述问题或写客套结尾。不得用感叹号。
- C4：事实和数字必须给出来源。
- C5：超过 300 字时，宜整理成文档或列表。对话宜只写结论和位置。
- C6：主动发起对话时，必须说清发生的事、通知时机和用户动作。
- C7：同一个结论必须只说一次。
- C8：不得把工具调用写成旁白。回复前必须自查措辞。只报告与任务有关的变化。
- C9：结构必须按内容选择。不得给简单回答套固定标题、模板或装饰图标。
- C10：任务交付与完整状态汇报必须按“任务回执”节写。

### D：任务文档

- D1：主语必须写名称。不得用人称代词代替名称。作者本人或本团队可省略主语。
- D2：必须先写结论，再写依据。每节第一句宜写本节结论。
- D3：一段必须只讲一个主题。一段宜不超过 6 句。
- D4：并列项或操作步骤达到 3 项时，必须写列表。步骤必须用编号列表。
- D5：每步必须只写一个动作，并以动词开头。说明必须与步骤分开写。
- D6：风险提示必须先写动作或条件，再写后果。
- D7：提醒必须用三级固定词：
    - “警告”：不可逆操作或安全问题。
    - “注意”：可能失败。
    - “说明”：背景补充。
- D8：代码注释必须写原因，不得复述代码。提交说明第一行必须写改动内容。

### I：提示词文件

- I1：强度词必须只用四组：
    - 必须 / 不得。
    - 宜 / 不宜。
    - 可 / 不必。
    - 能 / 不能。
- I2：不得把含糊的推荐词与“必须”连用。推荐要求必须用“宜”。
- I3：一条必须只写一个要求。例外必须与对应要求写在同一条。
- I4：必须写清触发条件、对象和动作。不得用含糊的时机代替触发条件。
- I5：要求和理由必须分开写。理由必须以“原因：”开头。
- I6：指称必须写名称、路径或编号。不得用含糊指代。
- I7：同一条要求必须只写一处。其他位置必须写指向。
- I8：要求必须写成能检查的形式。

### W：界面文案

当前无界面文案。新增界面文案时，必须执行 W1–W9。

- W1：不得用复数人称代词或第三人称代词。
- W2：“你”必须只指当前用户。“我”只能出现在用户原话中。“你”或“您”必须全站统一。
- W3：按钮必须以动词开头，宜不超过 6 字。同一动作必须全站用同一个推荐词。
- W4：同一功能必须在导航、标题、按钮、提示和帮助文档中同名。
- W5：报错必须说明发生的事和用户能做的下一步。不得只给错误码或责怪用户。
- W6：空状态必须说明将出现的内容和开始方法。
- W7：说明文字必须只解释内容或读法，不得写操作步骤。
- W8：一句界面文字必须用完整的字符串模板，不得拼接片段。
- W9：页面文字必须服务当前用户。制作标签、验收结论和设计取舍必须放开发记录。

### G：通用规则

- G1：一个意思必须只用一个词，不得轮换同义词。
- G2：产品名、功能名和指标名必须按“术语”节的术语表写。
- G3：必须用推荐词，并替换术语表列出的不推荐写法。
- G4：动作必须直接写成动词，不得用虚化动词加动作名词。
- G5：程度和数量必须写成数字或具体事实。没有依据时，必须写“【待补：…】”，不得编造。
- G6：不得用营销词、行话或套话。
- G7：不得用口号句式、对仗金句或顶针句。
- G8：缩写和代号首次出现时，必须附全称或解释。不得自造缩写。
- G9：一句必须只讲一件事。并列项达到 3 项时，必须写列表。
- G10：条件必须写在动作前。
- G11：必须用主动句。不需要说明行为者时，可用“被”字句。
- G12：一句宜不超过 40 字。操作步骤宜不超过 30 字。
- G13：名词前的修饰语必须不超过 3 层。
- G14：不得省略否定词或限定词。
- G15：必须保留表示把握程度和频率的词。
- G16：代词必须指向上文明确的名词。可能有歧义时，必须重复名称。
- G17：标点必须按 GB/T 15834—2011 写。引号必须用全角“”，不得用直角引号。
- G18：数字必须按 GB/T 15835—2011 写。计量和统计必须用阿拉伯数字，并带单位。
- G19：中文与英文、数字之间必须空一格，全项目统一。
- G20：每句话必须帮助当前读者理解、判断或操作：
    - 必须删除无关排除、制作说明和自证。
    - 必须保留价格、权限和安全边界。
- G21：必须用自然的完整句子。朗读不顺时，必须改写。
- G22：篇幅必须按任务需要确定。不得删掉必要步骤或风险信息。

## English (STE)

### Modes

| Text | Mode | Checks |
|---|---|---|
| Instruction files, user replies, error messages, status messages, and instructions between agents | `strict` | Enforce structure and word choice. |
| Task documents and descriptive prose | `STE-flavored` | Enforce structure, with the sentence limit below. Treat word choice as advisory. |

### Structure

- Use no more than 20 words in each instruction.
- In `strict` mode, use no more than 25 words in each descriptive sentence.
- In `STE-flavored` mode, the 25-word limit for descriptions is advisory. Use `--disable long-sentence` for the tool.
- Keep each noun cluster to no more than 3 words.
- Do not use semicolons.
- Keep each paragraph to no more than 6 sentences.
- Use lists for sequences and conditions.
- Put each condition before its action.
- Use active voice for procedures and instructions.
- When the actor is unknown or irrelevant to the reader, use passive voice only for descriptions.

### Parts of speech: advisory checks

Enforce these word rules in `strict` text.
In `STE-flavored` text, treat these rules as advisory.
The tool uses a small word list, not the full ASD-STE100 dictionary.
Tool checks for word choice are incomplete.

- Use one word for one sense.
- Use verbs instead of nouns for actions (Rule 3.7).
- Define each term once. Use `GLOSSARY.md` for terms in both languages.
- Do not use phrasal verbs (Rule 9.3). Use these replacements:
    - Replace `spin up` with `start`.
    - Replace `reach out` with `contact`.
    - Replace `check out` with `inspect` or `clone`, as the context requires.
    - Replace `point at` with `link` or `cite`, as the context requires.
- Inspect words that the tool does not check.

### Verb forms and tense exceptions

- Do not use the present perfect, past perfect, or compound tenses, except for the cases below:
    - When the source states uncertainty, keep `may/could have…`.
    - When a result is available now, keep `has completed`.
    - When an event occurred at a past time, use `completed`.
- Use `-ing` forms only as technical nouns.

### Rewrite discipline

- Keep all facts, conditions, qualifiers, negations, scope limits, uncertainty, and frequency.
- Keep the original modality, such as `must`, `may`, or `could`.
- Do not add facts that the source does not state.
- Do not rewrite text that already meets the rules.

## 混排切分

必须按 Markdown 块的语言选择规则：

- 标题、段落、列表项、表格单元格和引用块必须分别判定。
- 中文为主的块必须用 STC。中文句子中的英文术语仍归中文块。
- 英文为主的连续段必须用 STE，包括引用的英文原文。
- 围栏代码块和行内代码不进入两种语言的 lint。

检查工具必须把非目标语言块掩成空行。
原因：检查结果的行号必须与原文件一致。

## 任务回执

C10 回执必须分三段，按以下顺序写：

1. “做完了”：结果、产物位置和验证结果。
2. “需要你”：用户必须做的动作。
3. “知会”：用户不必行动的信息、限制或风险。

空段必须写“无”。
普通问答和进度通知必须按 C9 选择结构。

## lint 验证

运行环境必须有 Python 3 和 Node 18+。
包装脚本路径是 `.trellis/scripts/voice_lint.py`。
脚本由 voice-tooling 票交付。脚本可用后，必须执行本文件自检。
脚本暂不可用时，检查者必须按本文件逐项人工核对。

### 三式用法

检查当前改动文件：

```sh
python ./.trellis/scripts/voice_lint.py --changed
```

检查全量文件：

```sh
python ./.trellis/scripts/voice_lint.py --all
```

检查指定文件：
本文件自检使用此式。

```sh
python ./.trellis/scripts/voice_lint.py .trellis/spec/agents/voice.md tools/mp-trellis-pack/marketplace/specs/agent-workflow/agents/voice.md
```

### 棘轮规则

- 新写或改动的文件命中硬规则时，`--changed` 必须硬失败：
    - 基线必须为 0。
    - 退出码必须为 1。
    - 检查结果不得为 READY。
- 存量改造完成前，`--all` 对未改动的存量文件只报告警告，不阻断检查。
- 存量改造票完成后，`--all` 必须升级为硬失败：
    - STC 必须使用 `--max-errors 0`。
    - ste-lint 必须使用 `--baseline 0`。
- `passive-voice` 和 `present-perfect` 的 advisory 提示必须只进入报告，不阻断检查。
- G20 的相关性疑点必须只进入报告，不得启用 `--anti-echo` 硬闸。

advisory 提示不阻断检查，也不免除执行者的规则自查责任。

### 排除与自查

文件检查和存量改造必须跳过 `.trellis/tasks/archive/**`。
历史档案不得改写。

执行者必须自查机器不能完整判断的规则：

- 中文：G9 一句一事、C2 / D2 先写结论、G20 内容相关性。
- 英文：名词堆叠、词表外短语动词、词义、语态适用条件和时态例外。
- 改写：否定、限定、把握程度、频率和 modality（约束强度）必须保留。

## 术语

`GLOSSARY.md` 是项目唯一术语表。
中文名称、英文名称和定义必须按术语表写。
术语表的 `_Avoid_` 行是不推荐写法清单。
不得另建 STC `terms.yaml` 或独立英文词表。

## 例外清单

无。

## 署名

STC：CC-BY-4.0 © Daimonia（杭州代梦智能科技有限公司）。中文规则已裁剪。来源：`https://github.com/daimonia-ai/STC-Simplified-Technical-Chinese`。
ste-lint：MIT © 2026 Dustin Yuchen Teng。
STE 规则改写自 ASD-STE100 公开描述，经 asd-ste100-skill 整理。
