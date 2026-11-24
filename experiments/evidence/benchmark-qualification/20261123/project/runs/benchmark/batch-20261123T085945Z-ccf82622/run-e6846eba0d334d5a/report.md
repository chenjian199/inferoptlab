# Benchmark run

- Run: `run-e6846eba0d334d5a`
- State: `completed`
- Evidence: `measured`; validity: `valid`
- Performance SLA: `not_evaluated`; correctness/quality: `not_evaluated`
- Requests: {'planned': 4, 'observed': 4, 'succeeded': 4, 'failed': 0, 'missing': 0}
- Measurement duration: 1.530 s

| Metric | Mean | p50 | p90 | p95 | p99 | Samples |
|---|---:|---:|---:|---:|---:|---:|
| ttft | 37.705 | 32.025 | 48.643 | 52.053 | 54.781 | 4.000 |
| tpot | 22.867 | 22.850 | 22.902 | 22.913 | 22.922 | 4.000 |
| e2e_latency | 380.715 | 374.770 | 392.153 | 395.736 | 398.602 | 4.000 |
| input_tokens | 128.000 | 128.000 | 128.000 | 128.000 | 128.000 | 4.000 |
| output_tokens | 16.000 | 16.000 | 16.000 | 16.000 | 16.000 | 4.000 |

Latency units: ms; token-length units: tokens. Percentiles use successful requests; failures remain in the planned-request denominator. TPOT is not a true token-level ITL distribution.

| Rate | Value |
|---|---:|
| success_rate | 1.000 |
| request_throughput | 2.615 |
| input_token_throughput | 334.721 |
| output_token_throughput | 41.840 |

Observations / unresolved conditions:

- no SLA is attached to this diagnostic Case
