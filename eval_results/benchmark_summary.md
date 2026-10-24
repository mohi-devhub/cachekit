# Saved measured replay results

Generated only from the linked saved artifacts; median (min–max) across each run's repetitions.

| Metric | BEFORE | AFTER |
| --- | ---: | ---: |
| Requests per repetition | 27 | 27 |
| Repetitions | 3 | 3 |
| Measured cache-hit rate | 0.304% (0.304%–0.304%) | 80.690% (80.690%–80.690%) |
| Simulated cache-hit rate | 0.304% (0.304%–0.304%) | 80.690% (80.690%–80.690%) |
| Absolute prediction error | 0.000 pp (0.000 pp–0.000 pp) | 0.000 pp (0.000 pp–0.000 pp) |
| Client TTFT p50 | 2.014 s (1.996 s–2.076 s) | 1.425 s (1.404 s–1.472 s) |
| Client TTFT p95 | 2.557 s (2.523 s–3.362 s) | 2.475 s (1.756 s–2.524 s) |
| Request latency p50 | 3.032 s (2.978 s–3.111 s) | 2.635 s (2.554 s–3.268 s) |
| Request latency p95 | 4.998 s (4.804 s–5.180 s) | 4.072 s (3.866 s–4.374 s) |
| Completed requests / second | 0.281 (0.267–0.287) | 0.315 (0.314–0.315) |
| Allocated GPU-seconds / 1k | 3555.43 (3488.52–3751.57) | 3175.49 (3170.15–3186.90) |
| GPU-window USD / 1k | $0.7893 ($0.7745–$0.8328) | $0.7050 ($0.7038–$0.7075) |

Matched inputs, planned schedule, settings, price and profile: yes.

TTFT p50 change: -29.24% (negative means lower).
Measured cache reuse change: +80.386 percentage points.

One request is in flight. Planned arrivals can wait at the client; TTFT/latency
start at send time and exclude that queue delay. This is not an open-loop load test.
GPU seconds are allocated replay-window wall time, not GPU utilization. GPU-only
USD excludes startup, warmup/reset/idle, CPU, memory, storage and price modifiers.
It is not a full invoice. Model quality and human exact-diff approval are separate.

## Artifact identities

- [BEFORE](before_replay.json): SHA-256 `0a72b8f8c73329128c1c674e4cf8546ea665726cf8e56bf4eabe7d11bef35bda`.
  Source `bdddd55d54b1e6c1e058fa228316bd7cf7cbd7001fc259a0188045e6a316be89`; maximum client scheduling lag 50.801 s.
- [AFTER](after_confirmation_replay.json): SHA-256 `aa0084e09193aeba4d169f0e4005874755210270b8e60b45338ea8b78ca8fd7d`.
  Source `a2e81b98660ef4c7d59cb099cb961fc74e6b27fdce4497dc895eaf4798ab8aab`; maximum client scheduling lag 36.324 s.
