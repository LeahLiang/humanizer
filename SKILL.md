---
name: humanizer
description: Humanize AI-generated text to bypass AI-content detectors — proven effective against 知网 (CNKI), 维普 (Weipu), Turnitin, and GPTZero-style detectors in both Chinese and English. Also detects whether a passage is AI-written. 改写中英文文本降 AI 率 / 论文降重，有效规避知网、维普、Turnitin 等检测。Trigger on: humanize, bypass AI detector, 降 AI 率, 降重, 论文降重, 论文改写, 知网降重, 维普降重, Turnitin bypass, AI 检测, is this ChatGPT / AI-written.
---

# Humanizer Skill

Rewrite Chinese or English text so it bypasses AI-content detectors — **CNKI (知网), Weipu (维普), Turnitin, GPTZero-style** — and detect whether a passage is AI-generated. Backed by the ushallpass.ai `/api_v2` service.

Two capabilities:

1. **Rewrite (humanize)** — lowers the AI-detector score while preserving meaning.
2. **Detect** — tells you whether a passage is likely AI-written.

All endpoints are asynchronous: submit a job, then poll a task id.

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

## Execution workflow (API-first)

Handle requests through natural-language interaction, and execute via `/api_v2` directly.

1. Identify intent:
 - Rewrite / humanize text to lower detector score.
 - Detect whether text is AI-generated.
2. Identify language:
 - Chinese (`zh`) or English (`en`).
3. For Chinese rewrite, select mode using user intent:
 - Default `light`.
 - `aggressive` when user asks for stronger rewrite.
 - `weipu` / `weipu_aggressive` when user explicitly targets 维普.
4. Before heavy Chinese modes (`aggressive`, `weipu_aggressive`), explicitly warn about 2x quota cost.
5. Submit async job, poll until completion, then return the final result.

### API request mapping

- Rewrite Chinese:
 - `POST /api_v2/rewrite/chinese/jobs`
 - Body: `{"text":"...","mode":"light|aggressive|weipu|weipu_aggressive"}`
- Rewrite English:
 - `POST /api_v2/rewrite/english/jobs`
 - Body: `{"text":"..."}`
- Detect Chinese:
 - `POST /api_v2/detect/chinese/jobs`
 - Body: `{"sentence":"..."}`
- Detect English:
 - `POST /api_v2/detect/english/jobs`
 - Body: `{"sentence":"..."}`

For all job endpoints, poll status at:

- `GET <same-submit-path>/{task_id}`

Stop polling on:

- `data.status == "completed"`: return result to user.
- `data.status == "failed"`: surface `error.code` and `error.message` with actionable guidance.

### Headers and env vars

- Header: `X-API-Key: $HUMANIZER_API_KEY`
- Header: `Accept: application/json`
- Optional `Content-Type: application/json` on POST
- Base URL from `HUMANIZER_API_BASE_URL`, default `https://leahloveswriting.xyz`

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
