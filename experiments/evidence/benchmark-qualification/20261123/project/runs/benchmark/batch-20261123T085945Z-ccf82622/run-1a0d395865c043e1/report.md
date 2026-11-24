# Benchmark run

- Run: `run-1a0d395865c043e1`
- State: `completed`
- Evidence: `measured`; validity: `valid`
- Performance SLA: `not_evaluated`; correctness/quality: `not_evaluated`
- Requests: {'planned': 4, 'observed': 4, 'succeeded': 4, 'failed': 0, 'missing': 0}
- Measurement duration: 1.696 s

| Metric | Mean | p50 | p90 | p95 | p99 | Samples |
|---|---:|---:|---:|---:|---:|---:|
| ttft | 64.699 | 57.986 | 87.693 | 92.429 | 96.218 | 4.000 |
| tpot | 25.035 | 25.048 | 25.284 | 25.315 | 25.339 | 4.000 |
| e2e_latency | 840.785 | 835.247 | 855.748 | 859.307 | 862.154 | 4.000 |
| input_tokens | 1024.000 | 1024.000 | 1024.000 | 1024.000 | 1024.000 | 4.000 |
| output_tokens | 32.000 | 32.000 | 32.000 | 32.000 | 32.000 | 4.000 |

Latency units: ms; token-length units: tokens. Percentiles use successful requests; failures remain in the planned-request denominator. TPOT is not a true token-level ITL distribution.

| Rate | Value |
|---|---:|
| success_rate | 1.000 |
| request_throughput | 2.359 |
| input_token_throughput | 2415.388 |
| output_token_throughput | 75.481 |

Observations / unresolved conditions:

- no SLA is attached to this diagnostic Case
