# Saved measured replay results

Generated only from the linked saved artifacts; medians across each run's repetitions.

| Metric | BEFORE | AFTER |
| --- | ---: | ---: |
| Requests per repetition | 27 | 27 |
| Repetitions | 3 | 3 |
| Measured cache-hit rate | 0.304% | 80.622% |
| Simulated cache-hit rate | 0.304% | 80.622% |
| Absolute prediction error | 0.000 pp | 0.000 pp |
| Client TTFT p50 | 2.014 s | 1.527 s |
| Client TTFT p95 | 2.557 s | 2.099 s |
| Request latency p50 | 3.032 s | 2.780 s |
| Request latency p95 | 4.998 s | 4.268 s |
| Completed requests / second | 0.281 | 0.312 |
| Allocated GPU-seconds / 1k | 3555.43 | 3202.47 |
| GPU-window USD / 1k | $0.7893 | $0.7109 |

Matched inputs, planned schedule, settings, price and profile: yes.

TTFT p50 change: -24.18% (negative means lower).
Measured cache reuse change: +80.318 percentage points.

One request is in flight. Planned arrivals can wait at the client; TTFT/latency
start at send time and exclude that queue delay. This is not an open-loop load test.
GPU seconds are allocated replay-window wall time, not GPU utilization. GPU-only
USD excludes startup, warmup/reset/idle, CPU, memory, storage and price modifiers.
It is not a full invoice. Model quality and human exact-diff approval are separate.

## Artifact identities

- [BEFORE](before_replay.json): SHA-256 `0a72b8f8c73329128c1c674e4cf8546ea665726cf8e56bf4eabe7d11bef35bda`.
  Source `bdddd55d54b1e6c1e058fa228316bd7cf7cbd7001fc259a0188045e6a316be89`; maximum client scheduling lag 50.801 s.
- [AFTER](after_replay.json): SHA-256 `7c5492735af12717b9aa1588808a0fbe39fc9f247bce05191a79a7f1eb8b830a`.
  Source `3567620838e73ef4dc179d83583f39dde9bc8886ffa6a3393148c0e27313fb57`; maximum client scheduling lag 39.811 s.
