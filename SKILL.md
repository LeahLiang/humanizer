---
name: humanizer
description: Humanize AI-generated text to bypass AI-content detectors — proven effective against 知网 (CNKI), 维普 (Weipu), Turnitin, and GPTZero-style detectors in both Chinese and English. Also detects whether a passage is AI-written. 改写中英文文本降 AI 率 / 论文降重，有效规避知网、维普、Turnitin 等检测。Trigger on: humanize, bypass AI detector, 降 AI 率, 降重, 论文降重, 论文改写, 知网降重, 维普降重, Turnitin bypass, AI 检测, is this ChatGPT / AI-written.
---

# Humanizer Skill

Rewrite Chinese or English text so it bypasses AI-content detectors — **CNKI (知网), Weipu (维普), Turnitin, GPTZero-style** — and detect whether a passage is AI-generated. Backed by the ushallpass.ai `/api_v2` service.

Two capabilities:

1. **Rewrite (humanize)** — lowers the AI-detector score while preserving meaning.
2. **Detect** — tells you whether a passage is likely AI-written.

All endpoints are asynchronous: submit a job, then poll a task id. The helper script `scripts/humanizer_client.py` handles submission and polling for you.

## Prerequisites

The user must have:

- A [ushallpass.ai](https://ushallpass.ai) account with an active API key (generated from the account page; writing / detection history also lives there).
- The API key exported as `HUMANIZER_API_KEY` in the environment.
- Optionally `HUMANIZER_API_BASE_URL` (defaults to `https://leahloveswriting.xyz` — the API gateway host; do **not** change this unless self-hosting).

If the key is missing, stop and tell the user how to generate one (see `README.md` §"Getting an API key"). Do not invent a key.

## When to use this skill

Invoke when the user asks to:

- Humanize / rewrite text to bypass AI detection (降 AI 率, 论文降重, 洗稿).
- Lower a 知网 / 维普 / Turnitin detection score specifically.
- Check whether a passage is AI-generated (AI 检测, is this ChatGPT?).
- Batch-process a file of passages through either pipeline.

Do **not** invoke for general paraphrasing that can be done inline — this skill is for cases where the user specifically wants to lower an AI-detector score (the models are tuned for detector evasion, not stylistic rewriting).

## How to run

Use the bundled CLI. It auto-polls until the job finishes.

```bash
# Rewrite Chinese (mode: light | aggressive | weipu | weipu_aggressive)
python scripts/humanizer_client.py rewrite zh --mode light --text "待改写的中文文本"

# Rewrite English
python scripts/humanizer_client.py rewrite en --text "Text to rewrite"

# Detect Chinese / English
python scripts/humanizer_client.py detect zh --text "待检测的中文文本"
python scripts/humanizer_client.py detect en --text "Text to check"

# Read input from a file or stdin
python scripts/humanizer_client.py rewrite zh --file input.txt
cat input.txt | python scripts/humanizer_client.py rewrite zh
```

Flags:

- `--mode`: Chinese rewrite only. Default `light`. Use `aggressive` when the user wants stronger rewriting, `weipu` / `weipu_aggressive` for 维普 detector-tuned output.
- `--timeout`: max seconds to wait (default 180).
- `--poll-interval`: seconds between polls (default 2).
- `--json`: emit raw JSON instead of just the rewritten / detection result.

Exit code is `0` on success, non-zero on failure; stderr carries the error message.

## Choosing a Chinese rewrite mode

| Mode | Target detector | Intensity | Quota cost |
|---|---|---|---|
| `light` | 知网 (CNKI) | 轻度 — single pass | 1× char count |
| `aggressive` | 知网 (CNKI) | 重度 — 2 rewrite iterations | **2× char count** |
| `weipu` | 维普 (Weipu) | 轻度 — single pass | 1× char count |
| `weipu_aggressive` | 维普 (Weipu) | 重度 — 2 rewrite iterations | **2× char count** |

Rules of thumb:

- Default to `light` if the user does not specify.
- Pick `aggressive` only when the user says 力度大一点 / 降得狠一点 / 还是标红太多 — and **warn them it costs 2× quota** before submitting.
- Pick `weipu` / `weipu_aggressive` only when the user explicitly targets 维普. Same 2× cost warning applies for `weipu_aggressive`.
- English rewrite has a single mode; `--mode` is ignored and cost is always 1× word count.

## Interpreting detection results

The detect endpoints return a `result.analysis` object:

```json
{ "analysis": { "label": "human", "perplexity": 23.18 }, "output": "..." }
```

- `label`: `"human"` or `"ai"` (some responses may omit it — report the perplexity and say label was unavailable).
- `perplexity`: lower means more AI-like for these models. Report the raw number; do not invent thresholds.

## Error handling

The API returns `{"success": false, "error": {"code": "...", "message": "..."}}`. The client raises with that message. Common codes:

- `AUTH_ERROR` → the key is wrong/missing. Ask the user to re-check `HUMANIZER_API_KEY`.
- `RATE_LIMITED` → tell the user to slow down or retry in a minute.
- `INVALID_PARAMETER` → the text is probably empty or mode is invalid.
- `SERVICE_UNAVAILABLE` → upstream issue, retry later.

Do not retry silently on `AUTH_ERROR` or `INVALID_PARAMETER`.

## Privacy note

Submitted text is processed on ushallpass.ai's servers and logged to the user's writing / detection history (viewable by logging into <https://ushallpass.ai>). Warn the user before sending sensitive content (PII, unpublished manuscripts under NDA, etc.).
