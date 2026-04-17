---
name: humanizer
description: "Rewrite Chinese or English text to lower AI-detector scores for CNKI, Weipu, Turnitin, and GPTZero-style detectors. 改写中英文降 AI 率 / 论文降重。Trigger on: humanize, bypass AI detector, 降 AI 率, 降重, 论文降重, 论文改写, 知网降重, 维普降重, Turnitin bypass."
---

# Humanizer Skill

Rewrite Chinese or English text so it reads more human and lowers scores on **CNKI (知网), Weipu (维普), Turnitin, GPTZero-style** detectors. Backed by the ushallpass.ai `/api_v2` service.

Endpoints are asynchronous: submit a job, then poll by `task_id`.

## Prerequisites

The user must have:

- A [ushallpass.ai](https://ushallpass.ai) account with an active API key (from the account page; usage history also lives there).
- The API key exported as `HUMANIZER_API_KEY` in the environment.
- Optionally `HUMANIZER_API_BASE_URL` (defaults to `https://leahloveswriting.xyz` — the API gateway host; do **not** change this unless self-hosting).

If the key is missing, stop and tell the user how to generate one (see `README.md` §"Getting an API key"). Do not invent a key.

## When to use this skill

Invoke when the user asks to:

- Humanize / rewrite text to lower AI-detector scores (降 AI 率, 论文降重, 洗稿).
- Target 知网 / 维普 / Turnitin specifically.

Do **not** invoke for general paraphrasing that can be done inline — this skill is for cases where the user wants detector-oriented rewriting (tuned for that use case, not generic style edits).

## Execution workflow

1. Identify language: Chinese (`zh`) or English (`en`).
2. For Chinese rewrite, select mode from user intent:
   - Default `light`.
   - `aggressive` when the user wants a stronger rewrite.
   - `weipu` / `weipu_aggressive` when the user explicitly targets 维普.
3. Before heavy Chinese modes (`aggressive`, `weipu_aggressive`), explicitly warn about **2× quota** cost.
4. If the input is empty or whitespace-only, stop and ask the user for actual text instead of submitting a request.
5. Submit an async job, poll until completion, and return the final rewritten text. Return raw JSON only if the user asks.

### Minimal API contract

- Rewrite Chinese:
  - `POST /api_v2/rewrite/chinese/jobs`
  - Body: `{"text":"...","mode":"light|aggressive|weipu|weipu_aggressive"}`
- Rewrite English:
  - `POST /api_v2/rewrite/english/jobs`
  - Body: `{"text":"..."}`

Headers:

- `X-API-Key: $HUMANIZER_API_KEY`
- `Accept: application/json`
- `Content-Type: application/json` on POST

Poll status at:
- `GET <same-submit-path>/{task_id}`

Stop polling on:

- `data.status == "completed"`: return `result` (rewritten text) to the user.
- `data.status == "failed"`: surface `error.code` and `error.message` with actionable guidance.
- timeout / retry behavior should stay consistent with `scripts/humanizer_api.py`

Base URL comes from `HUMANIZER_API_BASE_URL`, default `https://leahloveswriting.xyz`.

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

## Error handling

The API returns `{"success": false, "error": {"code": "...", "message": "..."}}`. The client raises with that message. Common codes:

- `AUTH_ERROR` → the key is wrong/missing. Ask the user to re-check `HUMANIZER_API_KEY`.
- `RATE_LIMITED` → tell the user to slow down or retry in a minute.
- `INVALID_PARAMETER` → the text is probably empty or mode is invalid.
- `SERVICE_UNAVAILABLE` → upstream issue, retry later.

Do not retry silently on `AUTH_ERROR` or `INVALID_PARAMETER`.

## Privacy note

Submitted text is processed on ushallpass.ai's servers and may appear in the user's account history (viewable by logging into <https://ushallpass.ai>). Warn the user before sending sensitive content (PII, unpublished manuscripts under NDA, etc.).
