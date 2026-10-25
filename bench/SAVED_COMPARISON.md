# Saved replay comparison

`cachekit compare` formats two saved `BenchmarkRun` artifacts offline. It runs no
inference, needs no network and writes only the `--out` Markdown file.

```bash
uv run --no-sync cachekit compare eval_results/before_replay.json \
  eval_results/after_confirmation_replay.json --out comparison.md
```

The pair must pass `cachekit.benchmark_models.matched_replays`: BEFORE/AFTER
variants, the same recorded inputs, schedule, request count, settings, tokenizer,
price, deployment profile and three repetitions. Otherwise the command exits 1,
names the mismatches and writes nothing.

The table shows median (min–max) across repetitions, computed from each
repetition, for measured cache-hit rate, client TTFT p50/p95, request latency
p50/p95 and GPU-window USD per 1,000 requests, plus both artifact SHA-256 values.
A metric absent from any repetition is reported as missing, never as zero.

Limits: sequential replay with one request in flight; TTFT excludes the client
scheduling queue; cost is the GPU-window base-rate component only (no startup,
warmup, idle, CPU, memory or storage). It does not re-measure, recollect model
outputs or establish quality/behavioral acceptance.
