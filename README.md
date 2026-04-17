# humanizer — Claude Code Skill

**English** | [简体中文](README.zh-CN.md)

> Humanize AI-generated text and bypass AI-content detectors — proven effective against **CNKI (知网)**, **Weipu (维普)**, **Turnitin**, and **GPTZero-style** detectors.
>
> 改写中英文文本，规避知网 / 维普 / Turnitin 等 AI 检测器，用于论文降重 / 降 AI 率 / AI 内容检测。

A [Claude Code](https://claude.com/claude-code) skill that lets Claude rewrite passages to lower AI-detector scores and tell you whether a passage was AI-written, all via the `/api_v2` service behind [ushallpass.ai](https://ushallpass.ai).

- Works in Chinese **and** English.
- Uses the official async job API (submit → poll → result).
- Ships with a zero-dependency Python CLI (`humanizer_client.py`) that you can also use without Claude.

---

## Features

| Capability | Endpoint | Languages | Detectors it targets | Modes |
|---|---|---|---|---|
| Rewrite (humanize) | `POST /api_v2/rewrite/{chinese,english}/jobs` | zh / en | zh: 知网 (CNKI), 维普 (Weipu) · en: Turnitin, GPTZero-style | zh: `light`, `aggressive`, `weipu`, `weipu_aggressive` |
| Detect AI-generated | `POST /api_v2/detect/{chinese,english}/jobs` | zh / en | — | — |
| Health check | `GET /api_v2/health` | — | — | — |

---

## 1. Getting an API key

1. Register and log in at **<https://ushallpass.ai>** — this is where your account, quota, writing history and detection history live.
2. Open the account / settings panel and click **Generate API Key**.
3. Copy the plaintext key immediately — it is shown only once.
4. Export it in your shell:

   ```bash
   export HUMANIZER_API_KEY="ra_live_xxxxxxxxxxxxxxxx"
   ```

   Add the line to `~/.zshrc` / `~/.bashrc` to persist it.

> Each account keeps one active key. To rotate, hit the same endpoint with `{"rotate": true}`; the old key becomes invalid.
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

Just ask in natural language — Claude will pick the right command and mode.

- **Chinese rewrite (知网)** — *"帮我把下面这段降一下知网的 AI 率，力度大一点：……"*
  → Claude runs `rewrite zh --mode aggressive`.
- **Chinese rewrite (维普)** — *"针对维普改写下面这段……"*
  → Claude runs `rewrite zh --mode weipu` (or `weipu_aggressive`).
- **English rewrite (Turnitin / GPTZero)** — *"Humanize this paragraph to bypass Turnitin: ..."*
  → Claude runs `rewrite en`.
- **AI detection** — *"Check whether this paragraph was AI-written."*
  → Claude runs `detect zh` or `detect en`.

Claude polls the task for you and reports the finished output.

---

## 4. Standalone CLI usage

The Python script has zero dependencies beyond the standard library (Python 3.9+).

```bash
# Chinese rewrite (default mode: light — 知网轻度)
python scripts/humanizer_client.py rewrite zh --text "待改写的中文文本"

# Stronger Chinese rewrite (知网重度, costs 2x quota)
python scripts/humanizer_client.py rewrite zh --mode aggressive --text "……"

# 维普 modes
python scripts/humanizer_client.py rewrite zh --mode weipu --text "……"
python scripts/humanizer_client.py rewrite zh --mode weipu_aggressive --text "……"

# English rewrite (Turnitin / GPTZero-style)
python scripts/humanizer_client.py rewrite en --text "Text to humanize."

# Detect AI content
python scripts/humanizer_client.py detect zh --text "待检测的中文文本"
python scripts/humanizer_client.py detect en --text "Text to check."

# From file or stdin
python scripts/humanizer_client.py rewrite zh --file input.txt
cat input.txt | python scripts/humanizer_client.py rewrite en

# Full JSON response
python scripts/humanizer_client.py detect en --text "..." --json

# Health check
python scripts/humanizer_client.py health
```

### Global flags

| Flag | Default | Purpose |
|---|---|---|
| `--base-url` | `https://leahloveswriting.xyz` | Override if you self-host. Same as `HUMANIZER_API_BASE_URL`. |
| `--timeout` | `180` | Seconds to wait for the async task. |
| `--poll-interval` | `2` | Seconds between status checks. |
| `--json` | off | Emit raw JSON instead of just the result text. |

Exit codes: `0` success · `1` API / network error · `2` bad input.

---

## 5. Python library usage

```python
from scripts.humanizer_client import HumanizerClient

client = HumanizerClient()  # reads HUMANIZER_API_KEY from env

# Rewrite — zh, 知网重度
out = client.rewrite("待改写的中文文本", lang="zh", mode="aggressive")
print(out["result"])

# Detect — en
out = client.detect("Text to check.", lang="en")
print(out["result"]["analysis"])  # {"label": "human", "perplexity": 42.1}
```

---

## 6. Chinese rewrite modes

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

## 7. Error handling

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

## 8. Quotas & billing

Each API call runs through the account's normal quota. Usage, writing history and detection history are shared with the web app — log in at <https://ushallpass.ai> to audit everything and view the current pricing plan. Heavy Chinese rewrite modes (`aggressive`, `weipu_aggressive`) deduct **twice** the character count; see §6.

---

## 9. Privacy

Text you submit is processed on ushallpass.ai's servers and stored in your account's writing / detection history (viewable at <https://ushallpass.ai>). Do **not** send content you are contractually forbidden from sharing with third parties.

---

## 10. Repository layout

```
humanizer/
├── SKILL.md                        # Claude Code skill definition
├── README.md                       # This file
├── README.zh-CN.md                 # 简体中文版
├── LICENSE
└── scripts/
    └── humanizer_client.py         # CLI + Python client (no deps)
```

## License

MIT. See [LICENSE](LICENSE).

## Contributing

Issues and PRs welcome. This skill is community-maintained.
