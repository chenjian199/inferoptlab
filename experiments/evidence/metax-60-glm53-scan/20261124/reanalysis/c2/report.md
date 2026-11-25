# Benchmark run

- Run: `run-45fb66a83a5e4efe`
- State: `completed`
- Evidence: `measured`; validity: `valid`
- Performance SLA: `not_evaluated`; correctness/quality: `not_evaluated`
- Requests: {'planned': 8, 'observed': 8, 'succeeded': 8, 'failed': 0, 'missing': 0}
- Measurement duration: 20.420 s

| Metric | Mean | p50 | p90 | p95 | p99 | Samples |
|---|---:|---:|---:|---:|---:|---:|
| ttft | 375.851 | 374.887 | 428.104 | 457.521 | 481.054 | 8.000 |
| tpot | 151.924 | 151.943 | 153.170 | 153.551 | 153.856 | 8.000 |
| e2e_latency | 5085.481 | 5074.894 | 5117.767 | 5154.139 | 5183.236 | 8.000 |
| input_tokens | 128.000 | 128.000 | 128.000 | 128.000 | 128.000 | 8.000 |
| output_tokens | 32.000 | 32.000 | 32.000 | 32.000 | 32.000 | 8.000 |

Latency units: ms; token-length units: tokens. Percentiles use successful requests; failures remain in the planned-request denominator. TPOT is not a true token-level ITL distribution.

| Rate | Value |
|---|---:|
| success_rate | 1.000 |
| request_throughput | 0.392 |
| input_token_throughput | 50.147 |
| output_token_throughput | 12.537 |

Observations / unresolved conditions:

- no SLA is attached to this diagnostic Case
