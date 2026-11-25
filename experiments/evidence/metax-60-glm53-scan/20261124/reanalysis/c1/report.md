# Benchmark run

- Run: `run-d1822b2123064f45`
- State: `completed`
- Evidence: `measured`; validity: `valid`
- Performance SLA: `not_evaluated`; correctness/quality: `not_evaluated`
- Requests: {'planned': 4, 'observed': 4, 'succeeded': 4, 'failed': 0, 'missing': 0}
- Measurement duration: 19.342 s

| Metric | Mean | p50 | p90 | p95 | p99 | Samples |
|---|---:|---:|---:|---:|---:|---:|
| ttft | 224.398 | 209.109 | 252.948 | 262.324 | 269.825 | 4.000 |
| tpot | 148.709 | 148.636 | 149.041 | 149.088 | 149.125 | 4.000 |
| e2e_latency | 4834.390 | 4816.833 | 4873.179 | 4884.026 | 4892.704 | 4.000 |
| input_tokens | 128.000 | 128.000 | 128.000 | 128.000 | 128.000 | 4.000 |
| output_tokens | 32.000 | 32.000 | 32.000 | 32.000 | 32.000 | 4.000 |

Latency units: ms; token-length units: tokens. Percentiles use successful requests; failures remain in the planned-request denominator. TPOT is not a true token-level ITL distribution.

| Rate | Value |
|---|---:|
| success_rate | 1.000 |
| request_throughput | 0.207 |
| input_token_throughput | 26.471 |
| output_token_throughput | 6.618 |

Observations / unresolved conditions:

- no SLA is attached to this diagnostic Case
