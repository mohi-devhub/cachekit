"""Strict completion-stream collection. Persist digests/counts, not generated text."""

import hashlib
import json
from time import perf_counter

import httpx

from bench.models import RequestMeasurement


async def completion(
    client: httpx.AsyncClient,
    endpoint: str,
    payload: dict,
    *,
    request_id: str,
    origin: float,
    scheduled: float,
) -> RequestMeasurement:
    sent = perf_counter()
    first = None
    usage = None
    finish = None
    done = False
    output = hashlib.sha256()
    data = []
    async with client.stream("POST", endpoint + "/v1/completions", json=payload) as response:
        response.raise_for_status()
        if "text/event-stream" not in response.headers.get("content-type", ""):
            raise ValueError("Inference did not return an SSE stream")
        async for line in response.aiter_lines():
            if line.startswith(":"):
                continue
            if line.startswith("data:"):
                data.append(line[5:].lstrip())
                continue
            if line:
                continue  # SSE event/id fields carry no completion payload.
            if not data:
                continue
            raw, data = "\n".join(data), []
            if raw == "[DONE]":
                done = True
                break
            event = json.loads(raw)
            if "error" in event or event.get("model") != payload["model"]:
                raise ValueError("Inference stream error or mismatched model")
            choices = event.get("choices", [])
            if len(choices) > 1:
                raise ValueError("Expected one completion")
            for choice in choices:
                if choice.get("index") != 0 or not isinstance(choice.get("text"), str):
                    raise ValueError("Malformed completion event")
                text = choice["text"]
                if text:
                    if finish is not None:
                        raise ValueError("Output after finish marker")
                    if first is None:
                        first = perf_counter()
                    output.update(text.encode())
                if choice.get("finish_reason") is not None:
                    if finish is not None:
                        raise ValueError("Repeated finish marker")
                    finish = choice["finish_reason"]
            if event.get("usage") is not None:
                if usage is not None:
                    raise ValueError("Repeated final usage")
                usage = event["usage"]
    ended = perf_counter()
    if not done or data or first is None or usage is None or finish not in {"stop", "length"}:
        raise ValueError("Incomplete completion stream; no valid measurement")
    prompt, generated = usage.get("prompt_tokens"), usage.get("completion_tokens")
    if (
        type(prompt) is not int
        or prompt != len(payload["prompt"])
        or type(generated) is not int
        or not 0 < generated <= payload["max_tokens"]
    ):
        raise ValueError("Inference token usage does not match the request")
    details = usage.get("prompt_tokens_details") or {}
    cached = details.get("cached_tokens")
    if cached is not None and (type(cached) is not int or not 0 <= cached <= prompt):
        raise ValueError("Invalid cached-token usage")
    return RequestMeasurement(
        request_sha256=hashlib.sha256(request_id.encode()).hexdigest(),
        scheduled_s=scheduled,
        sent_s=sent - origin,
        first_token_s=first - origin,
        ended_s=ended - origin,
        ttft_s=first - sent,
        latency_s=ended - sent,
        scheduling_delay_s=max(0, sent - origin - scheduled),
        prompt_tokens=prompt,
        completion_tokens=generated,
        cached_tokens=cached,
        finish_reason=finish,
        output_sha256=output.hexdigest(),
    )
