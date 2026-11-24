# Benchmark comparison

Rows are independent runs. Comparison requires identical fingerprints AND verified environments with valid data. Unverified/incomplete/failed runs remain visible and are not eligible for ranking. No best-run selection or averaging of percentiles.

| Deployment | Scenario | Concurrency | Repeat | State | TTFT p95 ms | TPOT p95 ms | Output tokens/s | SLA | Comparison |
|---|---|---:|---:|---|---:|---:|---:|---|---|
| qwen-metax-vllm-attached | qwen-pipeline-smoke | 1.000 | 1.000 | completed | 52.053 | 22.913 | 41.840 | not_evaluated | 0b8178544def |
| qwen-metax-vllm-attached | qwen-pipeline-short | 1.000 | 1.000 | completed | 52.766 | 23.940 | 41.067 | not_evaluated | 6904b88487d3 |
| qwen-metax-vllm-attached | qwen-pipeline-short | 2.000 | 1.000 | completed | 92.429 | 25.315 | 75.481 | not_evaluated | 7ad4403095c3 |
| qwen-metax-vllm-attached | qwen-pipeline-long | 1.000 | 1.000 | completed | 224.368 | 24.133 | 33.437 | not_evaluated | d994201f2c44 |

Small exploratory request sets do not establish tail-latency confidence. Quality acceptance is a separate step.
