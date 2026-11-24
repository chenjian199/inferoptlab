# Benchmark run

- Run: `run-3fd9841d2a1d4137`
- State: `completed`
- Evidence: `measured`; validity: `valid`
- Performance SLA: `not_evaluated`; correctness/quality: `not_evaluated`
- Requests: {'planned': 4, 'observed': 4, 'succeeded': 4, 'failed': 0, 'missing': 0}
- Measurement duration: 3.117 s

| Metric | Mean | p50 | p90 | p95 | p99 | Samples |
|---|---:|---:|---:|---:|---:|---:|
| ttft | 40.898 | 36.242 | 49.916 | 52.766 | 55.046 | 4.000 |
| tpot | 23.758 | 23.726 | 23.903 | 23.940 | 23.969 | 4.000 |
| e2e_latency | 777.396 | 774.985 | 787.662 | 789.489 | 790.951 | 4.000 |
| input_tokens | 1024.000 | 1024.000 | 1024.000 | 1024.000 | 1024.000 | 4.000 |
| output_tokens | 32.000 | 32.000 | 32.000 | 32.000 | 32.000 | 4.000 |

Latency units: ms; token-length units: tokens. Percentiles use successful requests; failures remain in the planned-request denominator. TPOT is not a true token-level ITL distribution.

| Rate | Value |
|---|---:|
| success_rate | 1.000 |
| request_throughput | 1.283 |
| input_token_throughput | 1314.152 |
| output_token_throughput | 41.067 |

Observations / unresolved conditions:

- no SLA is attached to this diagnostic Case
