"""Provider adapters for the Multi-AI ontology benchmark.

Standard-library only. Secrets are read from environment variables by callers.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class ProviderError(RuntimeError):
    pass


def _post_json(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    *,
    timeout: int = 180,
) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ProviderError(f"HTTP {exc.code}: {detail[:2000]}") from exc
    except urllib.error.URLError as exc:
        raise ProviderError(f"Network error: {exc}") from exc
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ProviderError(
            f"Provider returned non-JSON HTTP payload: {raw[:2000]}"
        ) from exc


def extract_json_object(text: str) -> dict[str, Any]:
    candidate = text.strip()
    fence = chr(96) * 3
    if candidate.startswith(fence):
        lines = candidate.splitlines()
        if lines and lines[0].startswith(fence):
            lines = lines[1:]
        if lines and lines[-1].strip() == fence:
            lines = lines[:-1]
        candidate = "\n".join(lines).strip()
    try:
        parsed = json.loads(candidate)
        if not isinstance(parsed, dict):
            raise ProviderError("Model response JSON must be an object")
        return parsed
    except json.JSONDecodeError:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start >= 0 and end > start:
            try:
                parsed = json.loads(candidate[start : end + 1])
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
        raise ProviderError(f"Could not parse model JSON object: {text[:2000]}")


def call_openai_responses(
    *,
    base_url: str,
    api_key: str,
    model: str,
    system: str,
    prompt: str,
    timeout: int,
) -> tuple[str, dict[str, Any]]:
    payload = {
        "model": model,
        "instructions": system,
        "input": prompt,
        "temperature": 0,
    }
    data = _post_json(
        base_url.rstrip("/") + "/responses",
        payload,
        {"Authorization": f"Bearer {api_key}"},
        timeout=timeout,
    )
    texts = []
    for item in data.get("output", []):
        if item.get("type") != "message":
            continue
        for part in item.get("content", []):
            if part.get("type") in {"output_text", "text"} and part.get("text"):
                texts.append(part["text"])
    if not texts and isinstance(data.get("output_text"), str):
        texts.append(data["output_text"])
    if not texts:
        raise ProviderError(
            f"OpenAI Responses payload contained no output text: {str(data)[:2000]}"
        )
    return "\n".join(texts), data


def call_anthropic_messages(
    *,
    base_url: str,
    api_key: str,
    model: str,
    system: str,
    prompt: str,
    timeout: int,
) -> tuple[str, dict[str, Any]]:
    payload = {
        "model": model,
        "max_tokens": 2500,
        "temperature": 0,
        "system": system,
        "messages": [{"role": "user", "content": prompt}],
    }
    data = _post_json(
        base_url.rstrip("/") + "/v1/messages",
        payload,
        {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        timeout=timeout,
    )
    texts = [
        block["text"]
        for block in data.get("content", [])
        if block.get("type") == "text" and block.get("text")
    ]
    if not texts:
        raise ProviderError(
            f"Anthropic payload contained no text: {str(data)[:2000]}"
        )
    return "\n".join(texts), data


def call_gemini_generate_content(
    *,
    base_url: str,
    api_key: str,
    model: str,
    system: str,
    prompt: str,
    timeout: int,
) -> tuple[str, dict[str, Any]]:
    encoded_model = urllib.parse.quote(model, safe="-_.")
    url = (
        base_url.rstrip("/")
        + f"/v1beta/models/{encoded_model}:generateContent?key="
        + urllib.parse.quote(api_key, safe="")
    )
    payload = {
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0,
            "responseMimeType": "application/json",
        },
    }
    data = _post_json(url, payload, {}, timeout=timeout)
    texts = []
    for candidate in data.get("candidates", []):
        for part in candidate.get("content", {}).get("parts", []):
            if part.get("text"):
                texts.append(part["text"])
    if not texts:
        raise ProviderError(f"Gemini payload contained no text: {str(data)[:2000]}")
    return "\n".join(texts), data


def call_openai_compatible(
    *,
    base_url: str,
    api_key: str,
    model: str,
    system: str,
    prompt: str,
    timeout: int,
    json_mode: bool = True,
) -> tuple[str, dict[str, Any]]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    try:
        data = _post_json(
            url,
            payload,
            {"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )
    except ProviderError:
        if not json_mode:
            raise
        payload.pop("response_format", None)
        data = _post_json(
            url,
            payload,
            {"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )
    try:
        text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ProviderError(
            f"OpenAI-compatible payload contained no message text: {str(data)[:2000]}"
        ) from exc
    if not isinstance(text, str) or not text.strip():
        raise ProviderError("OpenAI-compatible message content is empty")
    return text, data


def call_provider(
    *,
    provider: str,
    base_url: str,
    api_key: str,
    model: str,
    system: str,
    prompt: str,
    timeout: int = 180,
    json_mode: bool = True,
) -> tuple[str, dict[str, Any]]:
    kwargs = dict(
        base_url=base_url,
        api_key=api_key,
        model=model,
        system=system,
        prompt=prompt,
        timeout=timeout,
    )
    if provider == "openai_responses":
        return call_openai_responses(**kwargs)
    if provider == "anthropic_messages":
        return call_anthropic_messages(**kwargs)
    if provider == "gemini_generate_content":
        return call_gemini_generate_content(**kwargs)
    if provider == "openai_compatible":
        return call_openai_compatible(**kwargs, json_mode=json_mode)
    raise ProviderError(f"Unsupported provider: {provider}")
