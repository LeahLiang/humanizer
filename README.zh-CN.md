# humanizer — Claude Code Skill

[English](README.md) | **简体中文**

> 改写中英文文本，规避 AI 内容检测——**对知网（CNKI）、维普（Weipu）、Turnitin、GPTZero 等检测器均有效**。
>
> Humanize AI-generated text to bypass CNKI / Weipu / Turnitin / GPTZero-style detectors, for both Chinese and English content.

一个 [Claude Code](https://claude.com/claude-code) 技能（Skill），让 Claude 直接调用 [ushallpass.ai](https://ushallpass.ai) 背后的 `/api_v2` 服务，帮你完成 **降 AI 率改写**（论文降重 / humanize）和 **AI 内容检测**。

- 支持中文、英文两种语言。
- 使用官方异步任务 API（提交 → 轮询 → 取结果）。
- 附带零依赖的 Python CLI (`humanizer_client.py`)，脱离 Claude 也能独立使用。

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
   export HUMANIZER_API_KEY="ra_live_xxxxxxxxxxxxxxxx"
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

---

## 4. 独立 CLI 使用

脚本仅依赖 Python 标准库（Python 3.9+）。

```bash
# 中文改写（默认模式：light — 知网轻度）
python scripts/humanizer_client.py rewrite zh --text "待改写的中文文本"

# 知网重度改写（消耗 2 倍字数）
python scripts/humanizer_client.py rewrite zh --mode aggressive --text "……"

# 维普模式
python scripts/humanizer_client.py rewrite zh --mode weipu --text "……"
python scripts/humanizer_client.py rewrite zh --mode weipu_aggressive --text "……"

# 英文改写（Turnitin / GPTZero 类）
python scripts/humanizer_client.py rewrite en --text "Text to humanize."

# AI 检测
python scripts/humanizer_client.py detect zh --text "待检测的中文文本"
python scripts/humanizer_client.py detect en --text "Text to check."

# 从文件或 stdin 读取
python scripts/humanizer_client.py rewrite zh --file input.txt
cat input.txt | python scripts/humanizer_client.py rewrite en

# 输出完整 JSON
python scripts/humanizer_client.py detect en --text "..." --json

# 健康检查
python scripts/humanizer_client.py health
```

### 全局参数

| 参数 | 默认值 | 作用 |
|---|---|---|
| `--base-url` | `https://leahloveswriting.xyz` | 自部署时覆盖，等价于 `HUMANIZER_API_BASE_URL` 环境变量。 |
| `--timeout` | `180` | 异步任务最长等待秒数。 |
| `--poll-interval` | `2` | 轮询间隔秒数。 |
| `--json` | 关 | 输出原始 JSON 而不是只打印结果文本。 |

退出码：`0` 成功 · `1` 接口 / 网络错误 · `2` 输入不合法。

---

## 5. 作为 Python 库使用

```python
from scripts.humanizer_client import HumanizerClient

client = HumanizerClient()  # 自动读取环境变量 HUMANIZER_API_KEY

# 改写（知网重度）
out = client.rewrite("待改写的中文文本", lang="zh", mode="aggressive")
print(out["result"])

# 检测
out = client.detect("Text to check.", lang="en")
print(out["result"]["analysis"])  # {"label": "human", "perplexity": 42.1}
```

---

## 6. 中文改写模式该怎么选

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

## 7. 错误处理

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

## 8. 配额与计费

每次接口调用都会按账号的正常额度扣费。调用记录、写作历史、检测历史与网站 To C 完全共用，可登录 <https://ushallpass.ai> 查询，资费也在该网站的定价页。中文重度改写模式（`aggressive`、`weipu_aggressive`）会扣两倍字数，详见 §6。

---

## 9. 隐私说明

提交的文本会在 ushallpass.ai 服务器上处理，并写入账号的写作 / 检测历史（可登录 <https://ushallpass.ai> 查看）。**请勿提交合同禁止外传的内容**（未公开稿件、含个人身份信息的数据等）。

---

## 10. 仓库结构

```
humanizer/
├── SKILL.md                        # Claude Code 技能定义
├── README.md                       # 英文版说明
├── README.zh-CN.md                 # 本文件（中文版）
├── LICENSE
└── scripts/
    └── humanizer_client.py         # CLI + Python 客户端（零依赖）
```

## License

MIT，见 [LICENSE](LICENSE)。

## 贡献

欢迎提 Issue 和 PR。本 Skill 由社区维护。
