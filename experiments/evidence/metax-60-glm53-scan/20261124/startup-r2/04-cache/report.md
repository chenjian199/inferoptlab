# Startup qualification

Scope: startup and exact-length API probes; not accuracy or performance acceptance.

| Deployment | TP / PP / DP / EP | Context | Token budget | Max sequences / DP | Status | Detail |
| --- | --- | ---: | ---: | ---: | --- | --- |
| glm53-vllm-a-cache | 8 / 1 / 1 / 1 | 32768 | 4096 | 128 | failed | cache replay does not satisfy declared per-request cache requirement |
