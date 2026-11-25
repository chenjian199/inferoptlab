# Startup qualification

Scope: startup and exact-length API probes; not accuracy or performance acceptance.

| Deployment | TP / PP / DP / EP | Context | Token budget | Max sequences / DP | Status | Detail |
| --- | --- | ---: | ---: | ---: | --- | --- |
| glm53-vllm-a-budget2048 | 8 / 1 / 1 / 1 | 32768 | 2048 | 128 | passed | 128→32, 16384→1 |
| glm53-vllm-a-budget8192 | 8 / 1 / 1 / 1 | 32768 | 8192 | 128 | passed | 128→32, 16384→1 |
| glm53-vllm-a-seqs64 | 8 / 1 / 1 / 1 | 32768 | 4096 | 64 | passed | 128→32, 16384→1 |
| glm53-vllm-a-seqs256 | 8 / 1 / 1 / 1 | 32768 | 4096 | 256 | passed | 128→32, 16384→1 |
| glm53-vllm-a-graph | 8 / 1 / 1 / 1 | 32768 | 4096 | 128 | passed | 128→32, 16384→1 |
