# Saved measured replay results

Generated only from the linked saved artifacts; medians across each run's repetitions.

| Metric | BEFORE | AFTER |
| --- | ---: | ---: |
| Requests per repetition | 27 | <pending> |
| Repetitions | 3 | <pending> |
| Measured cache-hit rate | 0.304% | <pending> |
| Simulated cache-hit rate | 0.304% | <pending> |
| Absolute prediction error | 0.000 pp | <pending> |
| Client TTFT p50 | 2.014 s | <pending> |
| Client TTFT p95 | 2.557 s | <pending> |
| Request latency p50 | 3.032 s | <pending> |
| Request latency p95 | 4.998 s | <pending> |
| Completed requests / second | 0.281 | <pending> |
| Allocated GPU-seconds / 1k | 3555.43 | <pending> |
| GPU-window USD / 1k | $0.7893 | <pending> |

Matched inputs, planned schedule, settings, price and profile: not established; no paired speedup claim.


One request is in flight. Planned arrivals can wait at the client; TTFT/latency
start at send time and exclude that queue delay. This is not an open-loop load test.
GPU seconds are allocated replay-window wall time, not GPU utilization. GPU-only
USD excludes startup, warmup/reset/idle, CPU, memory, storage and price modifiers.
It is not a full invoice. Model quality and human exact-diff approval are separate.

## Artifact identities

- [BEFORE](before_replay.json): SHA-256 `0a72b8f8c73329128c1c674e4cf8546ea665726cf8e56bf4eabe7d11bef35bda`.
  Source `bdddd55d54b1e6c1e058fa228316bd7cf7cbd7001fc259a0188045e6a316be89`; maximum client scheduling lag 50.801 s.
