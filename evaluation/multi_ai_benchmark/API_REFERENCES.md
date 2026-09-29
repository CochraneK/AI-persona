# Multi-AI Provider API References

Checked: 2026-09-21.

The benchmark keeps **model IDs configurable** because model names/version aliases change faster than the ontology protocol. Evidence-producing runs must archive the exact resolved model ID in `manifest.json`.

## OpenAI

Adapter: `openai_responses`

Reference:
- https://platform.openai.com/docs/quickstart/make-your-first-api-request
- https://developers.openai.com/api/docs/quickstart

Protocol used:
- Bearer API key;
- `POST /v1/responses`;
- `instructions` + `input`;
- output text extracted from response message content.

The adapter intentionally avoids hard-coding a model name.

## Anthropic / Claude

Adapter: `anthropic_messages`

Reference:
- https://platform.claude.com/docs/en/api/messages/create

Protocol used:
- `POST /v1/messages`;
- `x-api-key`;
- `anthropic-version: 2023-06-01`;
- system instruction + user message.

## Google Gemini

Adapter: `gemini_generate_content`

References:
- https://ai.google.dev/api/generate-content
- https://ai.google.dev/api

The current Google documentation recommends the newer Interactions API for new agentic projects, while `generateContent` remains supported. This benchmark uses `generateContent` because the task is a stateless, single-turn structured annotation call. The adapter is intentionally isolated so it can be migrated without changing benchmark semantics.

## Alibaba Cloud Model Studio / Qwen

Adapter: `openai_compatible`

References:
- https://help.aliyun.com/zh/model-studio/qwen-api-via-openai-chat-completions
- https://help.aliyun.com/zh/model-studio/compatibility-with-openai-responses-api

Qwen endpoints are region/workspace dependent, so `HO_QWEN_BASE_URL` is supplied via environment rather than committed.

## DeepSeek

Adapter: `openai_compatible`

Reference:
- https://api-docs.deepseek.com/api/create-chat-completion/

Default base URL in the example config:
- `https://api.deepseek.com`

The runner uses the OpenAI-compatible `/chat/completions` endpoint.

## Reproducibility rule

A benchmark result is not evidence unless the run manifest records:
- provider adapter;
- exact resolved model ID;
- run time;
- benchmark case hash;
- system prompt hash.

API keys are never written to the manifest or outputs.
