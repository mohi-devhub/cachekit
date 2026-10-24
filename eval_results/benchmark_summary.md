# Saved measured replay results

Generated only from the linked saved artifacts; median (min–max) across each run's repetitions.

| Metric | BEFORE | AFTER |
| --- | ---: | ---: |
| Requests per repetition | 27 | 27 |
| Repetitions | 3 | 3 |
| Measured cache-hit rate | 0.304% (0.304%–0.304%) | 80.599% (80.599%–80.599%) |
| Simulated cache-hit rate | 0.304% (0.304%–0.304%) | 80.599% (80.599%–80.599%) |
| Absolute prediction error | 0.000 pp (0.000 pp–0.000 pp) | 0.000 pp (0.000 pp–0.000 pp) |
| Client TTFT p50 | 2.014 s (1.996 s–2.076 s) | 1.319 s (1.316 s–1.347 s) |
| Client TTFT p95 | 2.557 s (2.523 s–3.362 s) | 1.671 s (1.570 s–1.937 s) |
| Request latency p50 | 3.032 s (2.978 s–3.111 s) | 2.272 s (2.269 s–2.291 s) |
| Request latency p95 | 4.998 s (4.804 s–5.180 s) | 3.664 s (3.602 s–3.692 s) |
| Completed requests / second | 0.281 (0.267–0.287) | 0.315 (0.313–0.316) |
| Allocated GPU-seconds / 1k | 3555.43 (3488.52–3751.57) | 3176.02 (3166.02–3195.04) |
| GPU-window USD / 1k | $0.7893 ($0.7745–$0.8328) | $0.7051 ($0.7029–$0.7093) |

Matched inputs, planned schedule, settings, price and profile: yes.

TTFT p50 change: -34.51% (negative means lower).
Measured cache reuse change: +80.295 percentage points.

One request is in flight. Planned arrivals can wait at the client; TTFT/latency
start at send time and exclude that queue delay. This is not an open-loop load test.
GPU seconds are allocated replay-window wall time, not GPU utilization. GPU-only
USD excludes startup, warmup/reset/idle, CPU, memory, storage and price modifiers.
It is not a full invoice. Model quality and human exact-diff approval are separate.

## Artifact identities

- [BEFORE](before_replay.json): SHA-256 `0a72b8f8c73329128c1c674e4cf8546ea665726cf8e56bf4eabe7d11bef35bda`.
  Source `bdddd55d54b1e6c1e058fa228316bd7cf7cbd7001fc259a0188045e6a316be89`; maximum client scheduling lag 50.801 s.
- [AFTER](after_replay.json): SHA-256 `0e0b532b99147149fd0fcddeb9c5425e1343764f690ad0dcf6437e3c00b5fc48`.
  Source `4a60ea8b1d9be129400f306f703808100a10a6dc961a4e2f6f92e29a50171b0c`; maximum client scheduling lag 28.833 s.
