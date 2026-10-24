"""Strict vLLM 0.31 token-counter snapshots; no inference or provider fallback."""

import json
import math
import re

from cachekit.models import BoundaryModel
from pydantic import Field

SAMPLE = re.compile(r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{(.*)\})?\s+(\S+)(?:\s+\d+)?$")
LABEL = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)="((?:[^"\\]|\\.)*)"(?:,|$)')
QUERIES = "vllm:prefix_cache_queries_total"
HITS = "vllm:prefix_cache_hits_total"


class CacheSnapshot(BoundaryModel):
    queries: int = Field(ge=0)
    hits: int = Field(ge=0)
    queries_created: float
    hits_created: float
    block_size: int = Field(gt=0)
    capacity_blocks: int = Field(gt=0)
    capacity_tokens: int = Field(gt=0)
    running: int = Field(ge=0)
    waiting: int = Field(ge=0)


def parse_metrics(text: str, model: str) -> CacheSnapshot:
    samples = []
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        match = SAMPLE.fullmatch(line)
        if not match:
            raise ValueError("Invalid Prometheus sample")
        name, raw_labels, raw_value = match.groups()
        labels, position = {}, 0
        for label in LABEL.finditer(raw_labels or ""):
            if label.start() != position or label[1] in labels:
                raise ValueError("Invalid or duplicate metric labels")
            labels[label[1]] = json.loads('"' + label[2] + '"')
            position = label.end()
        if position != len(raw_labels or ""):
            raise ValueError("Invalid metric labels")
        samples.append((name, labels, float(raw_value)))

    def single(name):
        selected = [
            (labels, value)
            for n, labels, value in samples
            if n == name and labels.get("model_name", model) == model
        ]
        if len(selected) != 1 or selected[0][0].get("engine") != "0":
            raise ValueError("Expected exactly one matching engine-0 metric: " + name)
        labels, value = selected[0]
        if not math.isfinite(value) or value < 0:
            raise ValueError("Invalid metric value: " + name)
        return labels, value

    def count(name):
        value = single(name)[1]
        if not value.is_integer():
            raise ValueError("Expected an integer token/request counter")
        return int(value)

    config, value = single("vllm:cache_config_info")
    if value != 1 or config.get("enable_prefix_caching") != "True":
        raise ValueError("Prefix caching is not enabled")
    if config.get("sliding_window") != "None" or config.get("is_attention_free") != "False":
        raise ValueError("Only full-attention cache profiles are supported")
    block, blocks, tokens = (
        int(config[k]) for k in ("block_size", "num_gpu_blocks", "kv_cache_size_tokens")
    )
    if block * blocks != tokens:
        raise ValueError("Unsupported grouped/hybrid KV capacity")
    result = CacheSnapshot(
        queries=count(QUERIES),
        hits=count(HITS),
        queries_created=single("vllm:prefix_cache_queries_created")[1],
        hits_created=single("vllm:prefix_cache_hits_created")[1],
        block_size=block,
        capacity_blocks=blocks,
        capacity_tokens=tokens,
        running=count("vllm:num_requests_running"),
        waiting=count("vllm:num_requests_waiting"),
    )
    if result.hits > result.queries:
        raise ValueError("Cache hits exceed queries")
    return result


def counter_delta(before: CacheSnapshot, after: CacheSnapshot) -> tuple[int, int]:
    identity = (
        "queries_created",
        "hits_created",
        "block_size",
        "capacity_blocks",
        "capacity_tokens",
    )
    if any(getattr(before, key) != getattr(after, key) for key in identity):
        raise ValueError("Server restarted or cache profile changed")
    queries, hits = after.queries - before.queries, after.hits - before.hits
    if queries < 0 or hits < 0 or hits > queries:
        raise ValueError("Cache counters reset or are inconsistent")
    return queries, hits
