"""Replay the stage-three plan before producing a non-executable handoff."""
from pathlib import Path

from analysis.planner import plan_tasks
from benchmark.common.io import file_hash, inside
from diagnosis.contracts import finish, header, validate
from tools.specs import SpecError, digest, read


REQUIREMENTS = {
    "evidence": "专项 trace、匹配基线与单因素实验，记录支持/推翻/不足及替代解释。",
    "baseline": "冻结模型、硬件、runtime、请求集、协议、源码 commit/补丁及镜像摘要。",
    "scope": "选择配置或代码路径；明确允许改动项、禁止改动项和真实调用边界。",
    "correctness": "固定参考实现、开发输入、误差/质量规则、状态及 aliasing 语义。",
    "acceptance": "独立验收器版本、固定工作点 E2E、回归用例及原始证据保存规则。",
    "budget": "分别限定候选数、GPU 秒、墙钟和 token；包含编译、预热、失败与验收。",
    "rollback": "恢复父配置/源码/镜像，检查不支持形状的 fallback，保留失败记录。",
}


def prepare(catalog, analysis_path):
    analysis_path = Path(analysis_path).resolve()
    source = read(analysis_path)
    if source.get("kind") != "AnalysisReport":
        raise SpecError("expected AnalysisReport")
    validate(catalog, source)
    plan = catalog.get(source["plan_ref"])
    if digest(plan) != source["plan_sha256"]:
        raise SpecError("analysis plan has changed")
    parent = source["diagnosis_artifact"]
    diagnosis_path = None
    if parent:
        diagnosis_path = inside(catalog.root, parent["path"])
        if file_hash(diagnosis_path) != parent["sha256"]:
            raise SpecError("diagnosis artifact has changed")
    # Reconstruct tasks, applicability, scope and evidence links instead of trusting
    # a user-editable 'passed' flag or a freshly recomputed document fingerprint.
    replay = plan_tasks(catalog, plan, diagnosis_path)
    if replay != source:
        raise SpecError("analysis report differs from its reproducible plan; regenerate stage three")
    tasks = []
    for task in source["tasks"]:
        state = {
            "needs_capture": "awaiting_evidence",
            "awaiting_baseline": "awaiting_baseline",
            "not_applicable": "not_applicable",
            "deferred_budget": "deferred_budget",
        }[task["status"]]
        method = task["method_snapshot"]
        tasks.append({
            "id": "handoff-" + task["id"],
            "analysis_task_id": task["id"],
            "method_ref": task["method_ref"],
            "status": state,
            "scope": task["scope"],
            "hypothesis_ids": task["hypothesis_ids"],
            "target": method["handoff"]["target"],
            "missing_evidence": task["missing_evidence"],
            "required_artifacts": method["handoff"]["required_artifacts"],
            "correctness_checks": method["correctness_checks"],
            "rollback": method["handoff"]["rollback"],
            "route": "undecided",
            "optimization_task": None,
            "candidate": None,
            "acceptance": None,
        })
    result = finish({
        **header("OptimizationHandoff", plan["id"] + "-handoff", "第四步：优化候选与验证交接"),
        "execution": "plan_only",
        "analysis_artifact": {"path": str(analysis_path), "sha256": file_hash(analysis_path)},
        "context_snapshot": source["context_snapshot"],
        "preflight_issues": source["preflight_issues"],
        "requirements": REQUIREMENTS,
        "tasks": tasks,
        "limitations": [
            "当前 AnalysisReport 是专项计划，不包含已执行的因果实验；不能导出可执行优化任务。",
            "配置候选、代码后端、资源租约、独立验收与自动回退执行器尚未实现。",
            "摘要及离线重放用于发现证据变化，不构成第三方真实性认证。",
        ],
    })
    validate(catalog, result)
    return result


def render(result):
    lines = ["# 第四步：优化交接", "", "状态：`plan_only`。尚未生成候选、启动 GPU 或作出验收结论。", "",
             "## 输入", "", f"专项报告：`{result['analysis_artifact']['path']}`", "",
             "## 前置问题", ""]
    lines.extend("- " + item for item in result["preflight_issues"])
    lines += ["", "## 共同交接要求", ""]
    lines.extend(f"- **{key}**：{value}" for key, value in result["requirements"].items())
    for task in result["tasks"]:
        lines += ["", f"## {task['analysis_task_id']}", "",
                  f"状态：`{task['status']}`；路线：`{task['route']}`。", "",
                  "优化方向：" + task["target"], "", "仍缺证据：", ""]
        lines.extend("- " + value for value in task["missing_evidence"])
        lines += ["", "交接制品：", ""]
        lines.extend("- " + value for value in task["required_artifacts"])
        lines += ["", "正确性：", ""]
        lines.extend("- " + value for value in task["correctness_checks"])
        lines += ["", "回退：" + task["rollback"]]
    lines += ["", "## 当前边界", ""]
    lines.extend("- " + value for value in result["limitations"])
    return "\n".join(lines) + "\n"
