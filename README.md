# Humanizer Skill

**简体中文** | [English](README.en.md)

> 改写中英文文本，规避 AI 内容检测——**对知网（CNKI）、维普（Weipu）、Turnitin、GPTZero 等检测器均有效**。
>
> Humanize AI-generated text to bypass CNKI / Weipu / Turnitin / GPTZero-style detectors, for both Chinese and English content.

一个 [Claude Code](https://claude.com/claude-code) 技能（Skill），让 Claude 直接调用 [ushallpass.ai](https://ushallpass.ai) 背后的 `/api_v2` 服务，帮你完成 **降 AI 率改写**（论文降重 / humanize）和 **AI 内容检测**。

- 支持中文、英文两种语言。
- 使用官方异步任务 API（提交 → 轮询 → 取结果）。
- 默认面向 Claude 对话使用；附带 Python CLI（可选，仅供开发者脚本化调用）。

---

## 功能一览

| 能力 | 接口 | 语言 | 针对检测器 | 模式 |
|---|---|---|---|---|
| 改写（降 AI 率） | `POST /api_v2/rewrite/{chinese,english}/jobs` | 中 / 英 | 中文：知网 (CNKI)、维普 (Weipu) · 英文：Turnitin、GPTZero 类 | 中文：`light`、`aggressive`、`weipu`、`weipu_aggressive` |
| AI 内容检测 | `POST /api_v2/detect/{chinese,english}/jobs` | 中 / 英 | — | — |
| 健康检查 | `GET /api_v2/health` | — | — | — |

---

## 1. 获取 API Key

1. 在 **<https://ushallpass.ai>** 注册并登录——账号、额度、写作历史、检测历史都在这里。
2. 打开账户 / 设置面板，点击 **生成 API Key**。
3. **立即**复制明文 key——它只会显示一次。
4. 在 Shell 中导出为环境变量：

   ```bash
   export HUMANIZER_API_KEY="<粘贴你在 ushallpass.ai 生成的 key>"
   ```

   建议写入 `~/.zshrc` / `~/.bashrc` 持久化。

> 每个账号只保留一把 active key。若想轮换，向同一接口传 `{"rotate": true}`，旧 key 会立即失效。
>
> **关于 API base URL**：账号后台在 `ushallpass.ai`，但 API 本身的域名是 `https://leahloveswriting.xyz`（环境变量 `HUMANIZER_API_BASE_URL` 的默认值）。一般情况不需要修改。

---

## 2. 把 Skill 安装到 Claude Code

克隆到 Claude Code 的 skills 目录（用户级或项目级都行）：

```bash
# 用户级（所有项目都能用）
mkdir -p ~/.claude/skills
git clone https://github.com/LeahLiang/humanizer.git ~/.claude/skills/humanizer

# 或者项目级（只在当前仓库生效）
mkdir -p .claude/skills
git clone https://github.com/LeahLiang/humanizer.git .claude/skills/humanizer
```

验证加载成功：

```
/skills
```

看到列表里有 `humanizer` 就说明成功了。之后当你说 "帮我把这段降一下知网的 AI 率"、"这段是不是 AI 写的" 之类的话，Claude 会自动调起这个 Skill。

---

## 3. 在 Claude Code 里怎么用

直接用自然语言说，Claude 会自己选命令和参数。

- **中文改写（知网）** —— *"帮我把下面这段降一下知网的 AI 率，力度大一点：……"*
  → Claude 会执行 `rewrite zh --mode aggressive`。
- **中文改写（维普）** —— *"针对维普改写下面这段……"*
  → Claude 会执行 `rewrite zh --mode weipu`（或 `weipu_aggressive`）。
- **英文改写（Turnitin / GPTZero）** —— *"Humanize this paragraph to bypass Turnitin: ..."*
  → Claude 会执行 `rewrite en`。
- **AI 检测** —— *"帮我检查这段是不是 AI 写的"*
  → Claude 会执行 `detect zh` 或 `detect en`。

Claude 会替你轮询任务、等结果、再把最终内容回显出来。

你可以直接像用户那样说：

- `帮我降低下面这段话的 AIGC 率：……`
- `针对维普改写下面这段，力度大一点：……`
- `Humanize this paragraph to bypass Turnitin: ...`

---

## 4. 改写示例

### 英文改写（Turnitin / GPTZero 风格）

**改写前：**

> Gliomas are the most common and aggressive type of primary brain tumors, arising from glial cells in the central nervous system (CNS). These tumors are classified by the World Health Organization (WHO) into grades I to IV, with glioblastoma multiforme (GBM) being the most malignant and deadly form. Despite advances in medical science, the prognosis for glioma patients remains poor, with median survival rates often less than two years for high-grade gliomas such as GBM.

**改写后：**

> Patients with primary brain tumors may also develop lymphomas, which are aggressive and commonly develop as a result of abnormal growth of these cells by their own immune system. The World Health Organization (WHO) categorizes these tumors into grades I to IV, and glioblastoma multiforme (GBM) is the most severe and lethal form. Poor prognosis is still an issue in patients with glioma, as median survival rates for high-grade gliomas like GBM are often less than two years, despite progress in medical science.

### 中文改写（知网 / 维普）

**改写前：**

> 本研究的目的在于探索创新激励机制，以激发知识型员工潜能，提升企业的竞争力。通过深入了解知识型员工的特点和需求，结合现代管理理念和方法，构建一套科学、合理、有效的激励机制。具体而言，我们希望通过创新激励机制，为知识型员工提供更多的发展机会和空间满足他们的自我实现需求；同时，通过激励机制的优化，提高知识型员工的工作积极性和创新能力为企业创造更多的价值。例如，我们可以借鉴一些成功企业的经验。这些企业通过采用灵活的工作制度、丰富的培训资源以及多元化的激励方式，成功吸引和留住了大量的知识型人才，提升了企业的核心竞争力。

**改写后：**

> 为挖掘脑力劳动者内在动力并强化公司市占优势，本项目着力设计一套能让奖励措施真正落地的方案。我们查阅了大量一线技术人员与管理人员的访谈记录，摒弃陈旧的管人思维，转而锚定这群人对晋升通道与专业尊严的渴求。由于单纯的薪资加总很难换来持久的创造力，本方案尝试将股权期权与项目决策权深度捆绑，使员工在攻克技术难关时能直接获得可见的权限。这种改变立竿见影。借鉴华为等实体工业龙头的做法，管理层可以尝试推行弹性的弹性工时制度，并向核心团队开放前沿实验室的设备使用权，从而依靠硬性资源的倾斜留住稀缺专家，最终让企业在市场博弈中占据技术高位。

---

## 5. 中文改写模式该怎么选

每个模式由两件事决定：**针对哪个检测器**，以及**改写力度**（跑几轮）。

| 模式 | 针对检测器 | 改写力度 | 扣费 |
|---|---|---|---|
| `light` | 知网（CNKI） | 轻度 — 单轮改写 | **1×** 字数 |
| `aggressive` | 知网（CNKI） | 重度 — 两轮迭代改写 | **2×** 字数 |
| `weipu` | 维普（Weipu） | 轻度 — 单轮改写 | **1×** 字数 |
| `weipu_aggressive` | 维普（Weipu） | 重度 — 两轮迭代改写 | **2×** 字数 |

> ⚠ **重度模式（`aggressive` / `weipu_aggressive`）会扣两倍字数**。比如 1000 字的文本重度改写要消耗 2000 字额度。建议先用对应的 `light` / `weipu` 跑一遍，若检测分仍然偏高再升级到重度模式，避免浪费额度。

英文改写只有一种模式，`--mode` 参数会被忽略，扣费恒为 1× 词数，英文针对 Turnitin 和 GPTZero 类检测器优化。

---

## 6. 错误处理

接口错误格式：`{"success": false, "error": {"code": ..., "message": ...}}`，客户端会抛出 `HumanizerError` 并带上 `code`。

| 错误码 | 含义 |
|---|---|
| `AUTH_ERROR` | API Key 缺失或无效。 |
| `FORBIDDEN` | Key 没有对应 scope。 |
| `INVALID_REQUEST` | 请求体不是合法 JSON。 |
| `INVALID_PARAMETER` | 必填字段缺失或参数非法。 |
| `RATE_LIMITED` | 触发限流，稍等再试。 |
| `TASK_SUBMIT_FAILED` / `TASK_STATUS_FAILED` | 上游队列 / 存储异常。 |
| `TASK_NOT_FOUND` | 任务不存在，或不属于当前 client。 |
| `SERVICE_UNAVAILABLE` | 上游模型服务不可用，稍后重试。 |
| `TIMEOUT`（客户端侧） | 任务未在 `--timeout` 内完成。 |

---

## 7. 配额与计费

每次接口调用都会按账号的正常额度扣费。调用记录、写作历史、检测历史与网站 To C 完全共用，可登录 <https://ushallpass.ai> 查询，资费也在该网站的定价页。中文重度改写模式（`aggressive`、`weipu_aggressive`）会扣两倍字数，详见 §5。

---

## 8. 隐私说明

提交的文本会在 ushallpass.ai 服务器上处理，并写入账号的写作 / 检测历史（可登录 <https://ushallpass.ai> 查看）。**请勿提交合同禁止外传的内容**（未公开稿件、含个人身份信息的数据等）。

---

## 9. 开发者附录：脱离 Claude 的独立用法（可选）

> 只有在你不用 Claude Code、想直接脚本化调用 API 时才需要看下面两节。

### CLI

```bash
# 改写
python scripts/humanizer_client.py rewrite zh --text "……"
python scripts/humanizer_client.py rewrite zh --mode aggressive --text "……"
python scripts/humanizer_client.py rewrite en --text "Text to humanize."

# 检测
python scripts/humanizer_client.py detect zh --text "待检测的中文文本"

# 从文件读取 / 输出完整 JSON
python scripts/humanizer_client.py rewrite zh --file input.txt
python scripts/humanizer_client.py detect en --text "..." --json
```

全局参数：`--base-url`（默认 `https://leahloveswriting.xyz`）、`--timeout`（默认 180s）、`--poll-interval`（默认 2s）、`--json`。退出码：`0` 成功 / `1` 接口或网络错误 / `2` 输入不合法。

### Python 库

```python
from scripts.humanizer_client import HumanizerClient

client = HumanizerClient()  # 读取 HUMANIZER_API_KEY 环境变量
print(client.rewrite("……", lang="zh", mode="aggressive")["result"])
print(client.detect("Text to check.", lang="en")["result"]["analysis"])
```

---

## 10. 仓库结构

```
humanizer/
├── SKILL.md                        # Claude Code 技能定义
├── README.md                       # 本文件（中文版）
├── README.en.md                    # English
├── LICENSE
└── scripts/
    └── humanizer_client.py         # CLI + Python 客户端（零依赖）
```

## License

MIT，见 [LICENSE](LICENSE)。

## 贡献

欢迎提 Issue 和 PR。本 Skill 由社区维护。
