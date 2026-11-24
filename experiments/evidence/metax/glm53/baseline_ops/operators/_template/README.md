# 算子契约模板

`contract.json` 为 template 状态。复制到新 operator ID 后，填写真实模块/dispatcher/kernel、phase、rank、shape、dtype、stride、alias、scale、state 与 workspace 契约；字段缺失时不得进行等价性验收。

大输入张量存服务器 artifact 目录并记录哈希。先证明 B0 重放一致，再实现 reference/candidate。局部性能必须同时覆盖 kernel 和必要 wrapper 开销；逐 shape 回退、未覆盖路径及 fallback 都进入报告。
