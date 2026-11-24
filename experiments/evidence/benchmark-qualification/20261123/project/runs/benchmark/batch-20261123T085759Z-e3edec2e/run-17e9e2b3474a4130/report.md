# Benchmark run

- Run: `run-17e9e2b3474a4130`
- State: `failed`
- Evidence: `measured`; validity: `incomplete`
- Performance SLA: `not_evaluated`; correctness/quality: `not_evaluated`
- Requests: {'planned': 4, 'observed': 0, 'succeeded': 0, 'failed': 4, 'missing': 4}
- Measurement duration: — s

| Metric | Mean | p50 | p90 | p95 | p99 | Samples |
|---|---:|---:|---:|---:|---:|---:|
| ttft | — | — | — | — | — | 0.000 |
| tpot | — | — | — | — | — | 0.000 |
| e2e_latency | — | — | — | — | — | 0.000 |
| input_tokens | — | — | — | — | — | 0.000 |
| output_tokens | — | — | — | — | — | 0.000 |

Latency units: ms; token-length units: tokens. Percentiles use successful requests; failures remain in the planned-request denominator. TPOT is not a true token-level ITL distribution.

| Rate | Value |
|---|---:|
| success_rate | 0.000 |
| request_throughput | — |
| input_token_throughput | — |
| output_token_throughput | — |

Observations / unresolved conditions:

- 4 planned requests have no terminal record
- complete measurement duration unavailable; throughput/goodput not inferred from process wall time
- per-request AIPerf export is missing
- AIPerf aggregate export is missing
- warmup failed or exceeded deadline
- no SLA is attached to this diagnostic Case
