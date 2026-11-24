# GLM greedy 重复性问题记录

观察日期：2026-11-23。适用范围：8卡C500，驱动3.8.30；vLLM `5df63a7203cdb9328d824a27b682e77c7b9928be`、MetaX `0962c8735ffe4795800030680311410848512b82` 加冻结适配补丁；固定镜像 `9bbf20db`，TP8/V2/eager、单请求、greedy。

## 历史9题greedy分叉尚未复现

状态：**待定位，未修复**。历史HumanEval smoke32与full164的交集中，10、37、89、94、123、144、148、156、162共9题输出不同；37还出现解析失败与通过的变化。保留原153/164基线，不改gold、不把变化题当作退化豁免。

四个独立plain引擎（含原版生成脚本对照）六轮32题均31/32，逐token一致。108次固定前缀诊断实际温度均0，sampler均取argmax，无并列最大值；162组同路径比较的logits及已采集模块输出完全一致。prefill/cached在7题出现数值差异，但未改变argmax，不能据此归因历史分叉。综合历史与本轮，32题内已有12题出现过不同输出，不能只监控原9题。

原历史运行没有保存首处分歧的完整logits/中间状态；本轮未重放完整full164请求历史，也未做冷/热编译缓存因果对照。没有证据证明随机采样、某个GEMM、KDA或通信算子存在错误。有限样本稳定不证明全局确定性。

后续算子回归采用同期B0/C、固定输入token/版本/调度/评分；稳定通过题不许退化，波动题下降待定位；局部算子和固定前缀数值验证独立进行。32题只筛查，正式验收仍需各三个独立进程完整164题。本轮没有设定通用浮点容差。

正文依据：[原实验报告](../../../../../../../experiments/evidence/metax/glm53/repeatability_20261123/REPORT.md)、[回归规则](../../../../methods/regression-policy.md)。审阅证据：[重复汇总](evidence/repeatability_summary.json)、[数值汇总](evidence/tensor_summary.json)、[原版脚本对照](evidence/legacy_comparison.json)。原路径、SHA256和摘录规则见 [artifacts.json](artifacts.json)。完整张量只在远程归档，未下载入知识库。
