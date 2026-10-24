# Explicit measurement runners

The deterministic engine never imports these inference clients. Raw input files
stay local or in your Modal workspace. Benchmark results retain hashes, timings
and counters; golden results retain only the fixed public synthetic cases.

## Serve the pinned model

Use the separately installed Modal CLI (no model weights are downloaded locally):

```sh
modal deploy bench/modal_vllm.py
```

This defines the selected unquantized Qwen model on one L4, using the revision,
vLLM version and context limit recorded in the project configuration. The server
reuses the `huggingface-cache` and `vllm-cache` volumes. It does not autoscale beyond
one container; use it exclusively for the benchmark. The deployment prints its
endpoint URL. It can return 503 during cold startup.

The server is intentionally unauthenticated during this experiment. Its middleware
allows only health/version/model lookup, completions, metrics and prefix reset.
Other vLLM development routes are blocked. Prefix reset needs
`VLLM_SERVER_DEV_MODE=1` in this pinned release; never expose the unrestricted
development server. Do not redeploy or share its endpoint while collecting.

Stop it as soon as the collection block finishes:

```sh
modal app stop --yes cachekit-benchmark
```

Idle scale-down is a fallback, not a substitute for stopping the deployment.

## Inspect, then replay

Run from the repository root in the project environment. Substitute the endpoint
printed by deployment and an actual identifier for that deployment:

```sh
uv run --no-sync python -m bench.replay inspect \
  --endpoint https://YOUR-SERVER.modal.direct \
  --deployment-id YOUR-DEPLOYMENT-ID \
  --out eval_results/local/deployment.json

uv run --no-sync python -m bench.replay run \
  --input data/demo/requests_before.jsonl --variant before \
  --recorded-inputs data/demo/inputs.jsonl \
  --endpoint https://YOUR-SERVER.modal.direct \
  --deployment-manifest eval_results/local/deployment.json \
  --exclusive-server --out eval_results/local/before_replay.json
```

Inspection waits for readiness with bounded backoff, treating startup 503 as
not-ready, and checks live version, model, context, block
size and KV capacity. Revision and GPU identity come from the operator's pinned
deployment; this is not cryptographic hardware/model attestation. If live capacity
changes, use it to configure analysis before preparing a fresh fix task. The
quality collector requires the exact task profile.

Replay sends exact locally rendered token IDs to `/v1/completions`, with the
recorded deterministic generation settings. It preserves timestamp order and uses relative arrival times as the planned
schedule. Only one request is in flight; overlapping arrivals wait at the client,
and that scheduling lag is recorded separately from TTFT and request latency.
This is a sequential trace replay, not an open-loop load or concurrency benchmark. Use the same `--arrival-scale` for BEFORE and AFTER.
Unsupported/mismatched settings or over-budget contexts fail instead of silently
changing requests. No inference request is retried.

Each repetition warms the model, settles its counters, resets the prefix cache,
then measures the traffic. The result contains all request timings, counter
snapshots, simulated versus measured reuse, and repetition median/min/max.
Request identifiers and generated output are hashed; raw prompts and answers
are omitted. Missing usage, truncated streams, unsuccessful resets, counter
resets or extra prompt-token traffic fail the run. The CLI writes a completed
artifact only after all requested repetitions succeed and refuses to overwrite
an existing result. A failed command does not produce a valid partial result.

`allocated_gpu_seconds_per_1000` is one allocated L4 multiplied by the replay
window's wall time, including scheduled gaps and client transport. It is not GPU
utilization or kernel execution time. `gpu_window_usd_per_1000` applies the
verified base GPU rate in `pricing.yaml`; it excludes startup, warmup, reset,
idle time, CPU, memory, storage and pricing modifiers. It is not a complete bill.
Unset pricing leaves USD absent. Do not publish it as total serving cost.

BEFORE and AFTER must have the same original-input hash, schedule hash and
settings to support a paired comparison. The simulator uses the live cache block
size/capacity, but remains prompt-only; generated tokens can cause real eviction
that it does not model. Concurrency/load sweeps remain deferred.

## Required behavioral guard

`quality.py` collects the fixed public E5-lite BEFORE/AFTER goldens on local vLLM
or Modal. Run `uv run --no-sync python -m bench.quality --help` for its arguments.
It uses the task's exact token IDs and generation settings and requires a live
server plus the deployment manifest above. `cachekit verify` consumes and
re-evaluates the saved artifact offline; it never starts inference. Missing,
stale, failed or unreviewed output differences prevent fix approval.

The existing `eval_results/modal_smoke.json` confirms serving and cache reuse
only. Mocked protocol tests are not published measurements. Actual golden
inference and an approved application fix are still pending.

Implementation references: [Modal server example](https://modal.com/docs/examples/vllm_inference),
[server scaling/lifecycle](https://modal.com/docs/guide/servers),
[pinned cache-reset response](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/entrypoints/serve/dev/cache/api_router.py),
[development-router registration](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/entrypoints/launchers/api_server/routers.py),
[token-counter definitions](https://github.com/vllm-project/vllm/blob/v0.31.0/vllm/v1/metrics/loggers.py),
and [Modal pricing](https://modal.com/pricing).
