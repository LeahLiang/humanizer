# Humanizer Skill

[简体中文](README.md) | **English**

> Humanize AI-generated text and bypass AI-content detectors — proven effective against **CNKI (知网)**, **Weipu (维普)**, **Turnitin**, and **GPTZero-style** detectors.
>
> 改写中英文文本，规避知网 / 维普 / Turnitin 等 AI 检测器，用于论文降重 / 降 AI 率 / AI 内容检测。

A [Claude Code](https://claude.com/claude-code) skill that lets Claude rewrite passages to lower AI-detector scores and tell you whether a passage was AI-written, all via the `/api_v2` service behind [ushallpass.ai](https://ushallpass.ai).

- Works in Chinese **and** English.
- Uses the official async job API (submit → poll → result).
- Ships with zero-dependency Python scripts (split core + CLI) that you can also use without Claude.

---

## Features

| Capability | Languages | Use case |
|---|---|---|
| Rewrite (lower AI score) | zh / en | Chinese targets CNKI and Weipu; English targets Turnitin and GPTZero-style detectors |
| Detect AI-generated content | zh / en | Check whether a passage is more likely AI-written and return analysis |
| Async handling built in | — | Claude handles submit → poll → final result automatically |

---

## 1. Getting an API key

1. Register and log in at **<https://ushallpass.ai>** — this is where your account, quota, writing history and detection history live.
2. Open the account / settings panel and click **Generate API Key**.
3. Copy the plaintext key immediately — it is shown only once.
4. Export it in your shell:

   ```bash
   export HUMANIZER_API_KEY="<paste-your-ushallpass-key-here>"
   ```

   Add the line to `~/.zshrc` / `~/.bashrc` to persist it.

> Each account keeps one active key. To rotate, open the account / settings panel on **ushallpass.ai** and **Generate API Key** again (do not use an API rotate call). Once the new key is issued, the old key stops working immediately.
>
> **Note on the API base URL.** The account / dashboard lives on `ushallpass.ai`, but the API itself is served from `https://leahloveswriting.xyz` (the default for `HUMANIZER_API_BASE_URL`). You do not need to change this unless self-hosting.

---

## 2. Install the skill in Claude Code

Clone into your Claude Code skills directory (either user-level or project-level):

```bash
# User-level (available in every project)
mkdir -p ~/.claude/skills
git clone https://github.com/LeahLiang/humanizer.git ~/.claude/skills/humanizer

# Or project-level (only in this repo)
mkdir -p .claude/skills
git clone https://github.com/LeahLiang/humanizer.git .claude/skills/humanizer
```

Verify it loaded:

```
/skills
```

You should see `humanizer` in the list. Claude will then invoke it automatically when the user asks things like *"帮我把这段降一下 AI 率"* or *"Humanize this paragraph to bypass Turnitin."*.

---

## 3. Usage through Claude Code

Just describe what you want in natural language. Claude chooses the mode and returns the result.

You can send prompts like:

- `Help me lower the AIGC score of this paragraph: ...`
- `Rewrite this for Weipu with stronger intensity: ...`
- `Humanize this paragraph to bypass Turnitin: ...`
- `Check whether this paragraph was AI-written: ...`

---

## 4. Examples

### English rewrite (Turnitin / GPTZero style)

**Before:**

> Gliomas are the most common and aggressive type of primary brain tumors, arising from glial cells in the central nervous system (CNS). These tumors are classified by the World Health Organization (WHO) into grades I to IV, with glioblastoma multiforme (GBM) being the most malignant and deadly form. Despite advances in medical science, the prognosis for glioma patients remains poor, with median survival rates often less than two years for high-grade gliomas such as GBM.

**After:**

> Patients with primary brain tumors may also develop lymphomas, which are aggressive and commonly develop as a result of abnormal growth of these cells by their own immune system. The World Health Organization (WHO) categorizes these tumors into grades I to IV, and glioblastoma multiforme (GBM) is the most severe and lethal form. Poor prognosis is still an issue in patients with glioma, as median survival rates for high-grade gliomas like GBM are often less than two years, despite progress in medical science.

### Chinese rewrite (CNKI / Weipu)

**Before:**

> 本研究的目的在于探索创新激励机制，以激发知识型员工潜能，提升企业的竞争力。通过深入了解知识型员工的特点和需求，结合现代管理理念和方法，构建一套科学、合理、有效的激励机制。具体而言，我们希望通过创新激励机制，为知识型员工提供更多的发展机会和空间满足他们的自我实现需求；同时，通过激励机制的优化，提高知识型员工的工作积极性和创新能力为企业创造更多的价值。例如，我们可以借鉴一些成功企业的经验。这些企业通过采用灵活的工作制度、丰富的培训资源以及多元化的激励方式，成功吸引和留住了大量的知识型人才，提升了企业的核心竞争力。

**After:**

> 为挖掘脑力劳动者内在动力并强化公司市占优势，本项目着力设计一套能让奖励措施真正落地的方案。我们查阅了大量一线技术人员与管理人员的访谈记录，摒弃陈旧的管人思维，转而锚定这群人对晋升通道与专业尊严的渴求。由于单纯的薪资加总很难换来持久的创造力，本方案尝试将股权期权与项目决策权深度捆绑，使员工在攻克技术难关时能直接获得可见的权限。这种改变立竿见影。借鉴华为等实体工业龙头的做法，管理层可以尝试推行弹性的弹性工时制度，并向核心团队开放前沿实验室的设备使用权，从而依靠硬性资源的倾斜留住稀缺专家，最终让企业在市场博弈中占据技术高位。

---

## 5. Chinese rewrite modes

Each Chinese rewrite mode is a combination of **which detector it targets** and **how hard it rewrites** (how many rewrite passes it runs).

| Mode | Target detector | Intensity | Quota cost |
|---|---|---|---|
| `light` | 知网 (CNKI) | 轻度 — single pass | **1×** char count |
| `aggressive` | 知网 (CNKI) | 重度 — 2 rewrite iterations | **2×** char count |
| `weipu` | 维普 (Weipu) | 轻度 — single pass | **1×** char count |
| `weipu_aggressive` | 维普 (Weipu) | 重度 — 2 rewrite iterations | **2×** char count |

> ⚠ **Heavy modes (`aggressive` / `weipu_aggressive`) deduct twice the character count from your quota.** A 1,000-character input costs 2,000 chars. Start from `light` / `weipu` and only escalate if the detector score is still too high.

English rewrite has a single mode — `--mode` is ignored and the cost is always 1× word count. English output is tuned against Turnitin and GPTZero-style detectors.

---

## 6. Error handling

The API returns errors as `{"success": false, "error": {"code": ..., "message": ...}}`. The client raises `HumanizerError` with the code.

| Code | Meaning |
|---|---|
| `AUTH_ERROR` | Missing or invalid API key. |
| `FORBIDDEN` | Key lacks the required scope. |
| `INVALID_REQUEST` | Body is not valid JSON. |
| `INVALID_PARAMETER` | Required field missing or value invalid. |
| `RATE_LIMITED` | Too many requests per minute — back off. |
| `TASK_SUBMIT_FAILED` / `TASK_STATUS_FAILED` | Upstream queue / storage error. |
| `TASK_NOT_FOUND` | Task id unknown or belongs to another client. |
| `SERVICE_UNAVAILABLE` | Upstream models are down. Retry later. |
| `TIMEOUT` (client-side) | Task did not finish within `--timeout`. |

---

## 7. Quotas & billing

Each API call runs through the account's normal quota. Usage, writing history and detection history are shared with the web app — log in at <https://ushallpass.ai> to audit everything and view the current pricing plan. Heavy Chinese rewrite modes (`aggressive`, `weipu_aggressive`) deduct **twice** the character count; see §5.

---

## 8. Privacy

Text you submit is processed on ushallpass.ai's servers and stored in your account's writing / detection history (viewable at <https://ushallpass.ai>). Do **not** send content you are contractually forbidden from sharing with third parties.

---

## 9. Standalone usage (optional)

> Only needed if you want to call the API directly without Claude Code.

### CLI

```bash
# Rewrite
python scripts/humanizer_client.py rewrite zh --text "..."
python scripts/humanizer_client.py rewrite zh --mode aggressive --text "..."
python scripts/humanizer_client.py rewrite en --text "Text to humanize."

# Detect
python scripts/humanizer_client.py detect zh --text "待检测的中文文本"

# From file / raw JSON output
python scripts/humanizer_client.py rewrite zh --file input.txt
python scripts/humanizer_client.py detect en --json --text "..."
```

Global flags: `--base-url` (default `https://leahloveswriting.xyz`), `--timeout` (180s), `--poll-interval` (2s), `--json`. `--json` can be passed before or after subcommands. Exit codes: `0` success / `1` API or network error / `2` bad input.

### Python library

```python
from scripts.humanizer_client import HumanizerClient

client = HumanizerClient()  # reads HUMANIZER_API_KEY from env
print(client.rewrite("...", lang="zh", mode="aggressive")["result"])
print(client.detect("Text to check.", lang="en")["result"]["analysis"])
```

---

## 10. Repository layout

```
humanizer/
├── SKILL.md                        # Claude Code skill definition
├── README.md                       # 简体中文版（默认）
├── README.en.md                    # This file
├── LICENSE
└── scripts/
    ├── humanizer_api.py            # API core (submit/poll/error handling)
    ├── humanizer_cli.py            # CLI argument parsing and output
    └── humanizer_client.py         # Compatibility entrypoint + exports
```

## License

MIT. See [LICENSE](LICENSE).

## Contributing

Issues and PRs welcome. This skill is community-maintained.
