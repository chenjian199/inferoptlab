# Benchmark run

- Run: `run-ac5a0fc3bd8a4b96`
- State: `completed`
- Evidence: `measured`; validity: `valid`
- Performance SLA: `not_evaluated`; correctness/quality: `not_evaluated`
- Requests: {'planned': 4, 'observed': 4, 'succeeded': 4, 'failed': 0, 'missing': 0}
- Measurement duration: 3.828 s

| Metric | Mean | p50 | p90 | p95 | p99 | Samples |
|---|---:|---:|---:|---:|---:|---:|
| ttft | 218.478 | 220.505 | 223.739 | 224.368 | 224.871 | 4.000 |
| tpot | 23.750 | 23.878 | 24.091 | 24.133 | 24.167 | 4.000 |
| e2e_latency | 954.714 | 956.659 | 968.151 | 968.889 | 969.480 | 4.000 |
| input_tokens | 8192.000 | 8192.000 | 8192.000 | 8192.000 | 8192.000 | 4.000 |
| output_tokens | 32.000 | 32.000 | 32.000 | 32.000 | 32.000 | 4.000 |

Latency units: ms; token-length units: tokens. Percentiles use successful requests; failures remain in the planned-request denominator. TPOT is not a true token-level ITL distribution.

| Rate | Value |
|---|---:|
| success_rate | 1.000 |
| request_throughput | 1.045 |
| input_token_throughput | 8559.849 |
| output_token_throughput | 33.437 |

Observations / unresolved conditions:

- no SLA is attached to this diagnostic Case
