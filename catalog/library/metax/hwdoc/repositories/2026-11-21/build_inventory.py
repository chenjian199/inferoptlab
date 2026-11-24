"""Offline curation of the captured GitHub metadata. No repository code is executed."""
import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
GROUPS = {
"推理与后训练": (['inference','training'], '''vLLM-metax|vLLM 的 MetaX 硬件插件；重点查看发布分支和匹配镜像
sglang|SGLang 推理框架 fork；顶层说明仍以上游为主
vllm-omni-metax|多模态多阶段推理适配插件，依赖 vllm-metax 后端
verl-metax|verl 的独立 MetaX 硬件插件，查看准确版本契约
Onnxruntime|ONNX Runtime 代码仓库；具体 MetaX 构建条件需查对应分支
ppl.llm.serving|PPL 大模型服务工程；具体平台适用性待核对
AIModels|SGLang PD 分离部署方案，包含 C500 等型号配套表
LMCache|KV Cache 管理框架 fork；默认 README 未确认 C500 条件
Mooncake|分布式 KV 缓存与传输引擎，README 提及 MACA 传输支持'''),
"框架与编译": (['development','training'], '''mcPytorch|PyTorch 的 MetaX 后端实现，默认 2.4；另有版本分支
mcTriton|Triton 算子编译器适配；与 Triton Inference Server 分开
mcTVM|TVM 编译框架 fork，默认 dev；适配范围需看具体子目录
mcApex|混合精度与分布式训练扩展；顶层 README 保留上游介绍
mcXformer|Transformer 算子与组件工程；顶层适配约束待核对
mxJitify|运行时编译辅助库；上游 CUDA 说明不能作为 C500 安装依据
mxNumbax|Numba 相关 Python 编译工程，默认 MACA 命名分支'''),
"算子与数学库": (['kernels','libraries'], '''mcoplib|MetaX 高性能算子库，README 含 vLLM/SGLang 配套关系
FlashMLA|MACA 上的 MLA/注意力实现，README 明确提及 C500/C600
mcFlashMLA|另一份 MACA FlashMLA 实现，README 明确提及 C500；单独保留
McFlashInfer|MACA 平台 LLM 推理算子及内核生成库
flashattn|FlashAttention 代码仓库；上游要求仍需区分
TileOPs-Metax|基于 TileLang 的 LLM 算子库 fork，默认 dev
TileKernels-Metax|基于 TileLang 的算子库 fork；默认 README 仍列 NVIDIA 要求
mcEigen|Eigen 线性代数工程；与本地 mcEigen 手册关联
mcSolver|MetaX GPU 加速矩阵分解与线性方程求解库
mcSparse|MetaX 稀疏线性代数基础库
mcTlass|仓库清单可见，常见根 README 未取得；用途和构建要求待确认
mcpy|数组计算生态工程，默认 MACA 命名分支
mcdf|DataFrame 数据处理生态工程，默认 MACA 命名分支
mcFaiss|向量相似度检索和聚类库 fork
mxCuco|并发数据结构相关工程；默认 MACA 命名分支
mxRmmx|GPU 内存管理工程，README 含 MACA_PATH 构建提示'''),
"通信与存储": (['communication'], '''mccl-nccl|MCCL 集合通信库工程，README 明确要求 MXMACA 环境
mccl_tests|MCCL 性能与通信测试工具；执行前确认资源影响
MXDeepEP|专家并行通信工程；顶层 README 保留上游 NVIDIA 条件
DeepEP|DeepEP 上游 fork；与 MXDeepEP 分开记录
mcfile-python|MACA mcFile 的 Python 接口
fio|增加 MACA libmcfile I/O 引擎的 fio 工程
mxFIO|MACA MAS 存储测试工程；与 fio 分开保留
3FS|分布式文件系统 fork，未从 README 确认 C500 适配'''),
"示例与性能实践": (['development','profiling','kernels'], '''maca-samples|MXMACA 基础 GPU 编程示例集合
gpuBenchmark|支持 MetaX/NVIDIA 的基准测试集合，具体数值不是本机结果
op_optimization|C500 与 TileLang 算子优化竞赛、指南入口
QuickGuide|根 README 只有标题，需进一步查看仓库内容'''),
"监控与工程工具": (['cloud','development'], '''mxExporter|基于 MXSML 的 MetaX GPU Prometheus 指标导出工具
pymxsml|MXSML Python 绑定，README 有 MXC500 示例输出
go-mxsml|MXSML Go 绑定
goutils|通用 Go 工具包，不等于 GPU 计算框架
mxDlrover|分布式训练管理 DLRover fork
simple-jenkins-githubaction|触发 Jenkins 的 CI Action；非模型运行依赖
MetaX-MACA.github.io|组织网页工程；常见根 README 未取得'''),
"AI4S 与科学计算": (['ai4s'], '''metax-ai4s|AI4S 领域总导航
AI4S-Framework|DeepXDE、PaddleScience、PhysicsNeMo 等适配方案集合
LifeScience|生命科学与蛋白质、分子应用集合
MedicalImage|医学影像模型与适配方案集合
Materials|材料科学模型与计算方案集合
GeoScience|地球科学模型与应用集合
Physics|物理仿真及科学机器学习框架集合
WeatherForecast|气象预报模型集合
metax-lifescience-toolkit|生命科学 Agent skills 工具包；本次只盘点，未安装技能
hpc_warp|Warp v1.8.1 的 MetaX 适配，README 指向配套镜像'''),
"应用解决方案": (['inference'], '''DocFlowAI|文档结构化与多模态解析方案
Embodied_AI_Simulation|具身智能仿真方案
Autonomous_Driving_Simulation|自动驾驶场景重建、编辑与数据增强方案
VirtualHuman|虚拟人应用迁移方案''')
}

NOTES = {
"vLLM-metax":"默认 master 跟踪上游；README 区分 master、dev、releases 分支，并要求 vLLM 与插件同版本。当前 README 的 Python>=3.12 不可套用官网历史 py310 镜像。",
"mcPytorch":"默认 2.4 不能代表全部版本；API 还列出 2.8.0-maca3.8.0 和 2.10.0-maca3.8.0。旧 README 镜像示例不得覆盖新 PDF/镜像约束。",
"mcTriton":"存在 3.0 与 3.6 分支；本次 README 取自默认 3.0，不能据此推定 3.6 构建要求。",
"mcoplib":"README 的配套表使用 release/v0.4.x 标签形式，API 实际分支为 mcoplib-0.4.x、Release tag 为 mcoplib_0.4.x；三者必须分开核对。",
"vllm-omni-metax":"当前 main README 指向 0.32.0 软件栈；官网快照中的 0.26.0 样例是另一版本，不能直接混装。",
"verl-metax":"README 的硬件验证是项目维护者声明，不是本服务器实测；要求 verl-metax 0.9.0 与 verl 0.9.0 对齐，并提示不要同时自动加载两个 MetaX 插件。",
"AIModels":"此仓库实际为 PD 分离方案，不能因名称相近而关联到 AI4S aimodels-maca 镜像。表中具体 SDK 要求仅针对对应 SGLang 行。",
"MXDeepEP":"根 README 仍列 Hopper/CUDA/NVLink/NVSHMEM；仓库另有 build.md 和 maca_tools，但本次未审计其源码或构建流程。C500 部署条件待核实。",
"DeepEP":"fork 与 MXDeepEP 是不同仓库；顶层 NVIDIA 要求不证明 C500 支持或不支持。",
"FlashMLA":"README 明确写 C500/C600，但本机仍待验证；不与 mcFlashMLA 合并成同一版本。",
"mcFlashMLA":"README 明确写 C500；与 FlashMLA 分开保留 commit、分支和条件。",
"TileKernels-Metax":"默认 dev README 列 NVIDIA SM90/SM100 与 CUDA13.1；仓库名中的 Metax 不足以证明该分支在 C500 可用。",
"TileOPs-Metax":"默认 dev README 主要为上游算子项目说明；尚未从顶层资料确认 C500 运行条件。",
"pymxsml":"MXC500 出现在示例输出中，属于示例线索，不是完整支持矩阵。",
"modelzoo":"保留历史入口；不得等同于官网当前各 ModelZoo 镜像。"
}


def main():
    raw = json.loads((ROOT/'raw_repositories.json').read_text(encoding='utf-8'))
    readmes = {r['name']:r for r in json.loads((ROOT/'readme_manifest.json').read_text(encoding='utf-8'))}
    detail = json.loads((ROOT/'focus_metadata.json').read_text(encoding='utf-8'))
    mapping = {}
    for group,(topics,content) in GROUPS.items():
        for line in content.splitlines():
            name,purpose=line.split('|',1)
            mapping[name]=(group,topics,purpose)
    mapping['modelzoo']=('示例与性能实践',['inference','training'],'历史 ModelZoo 导航和模型资源入口')
    assert set(mapping)=={r['name'] for r in raw}, (set(mapping) ^ {r['name'] for r in raw})
    records=[]
    for repo in raw:
        name=repo['name']; group,topics,purpose=mapping[name]; rm=readmes[name]
        text=(ROOT/rm['path']).read_text(encoding='utf-8',errors='replace') if rm['status']=='downloaded' else ''
        lines=text.splitlines()
        # Candidate lines are search clues, not automatically asserted support.
        clues=[{'line':i+1,'text':line[:1500]} for i,line in enumerate(lines)
               if re.search(r'C500|C550|C600|Hopper|SM90|SM100|CUDA 1[23]|硬件|Hardware|MC[XC]500',line,re.I)][:12]
        if not text.strip(): support='未取得根 README；未知'
        elif name=='pymxsml': support='README 有 MXC500 示例；非支持矩阵'
        elif name=='mcPytorch': support='README 有 MXC500 镜像示例；需匹配分支'
        elif name in {'FlashMLA','mcFlashMLA','AIModels','op_optimization'}: support='README 明确提及 C500；本机未验证'
        elif re.search(r'C-series|C系列|C-Series|C 系列',text):support='README 提及 C 系列；C500 具体组合待核对'
        elif re.search(r'MACA|MetaX|沐曦',text) and name not in {'goutils','simple-jenkins-githubaction'}:support='README 有 MetaX/MACA 线索；C500 条件待核对'
        else:support='顶层 README 未确认 C500 条件'
        d=detail.get(name)
        fields=['name','full_name','description','default_branch','fork','archived','disabled','pushed_at','updated_at','language','size','open_issues_count','topics']
        row={k:repo[k] for k in fields}
        row['github_topics']=row.pop('topics')
        row.update(source_url=repo['html_url'],metadata_url=repo['url'],category=group,topics=topics,purpose=purpose,
                   license_spdx=repo['license']['spdx_id'] if repo['license'] else None,
                   readme=rm,c500_assessment=support,c500_clues=clues,review_note=NOTES.get(name,''),
                   verification='repository_observed_not_built_or_run',
                   branch_observations=d['branches'] if d else None,
                   release_observations=d['releases'] if d else None)
        records.append(row)
    (ROOT/'repositories.json').write_text(json.dumps({'observed_on':ROOT.name,'repositories':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# MetaX-MACA 公开仓库清单','',f'采集日期：{ROOT.name}。共 {len(records)} 个公开仓库；来源为 GitHub API 与默认分支 README。',
           '', '[盘点结论](README.md) · [机器可读清单](repositories.json) · [覆盖范围](coverage.json)', '',
           'Fork 为 GitHub 元数据标记，不是适配完成度；非 Fork 也可能包含上游代码。pushed_at 是仓库推送时间，不是默认分支提交时间。',
           '许可证仅按 GitHub SPDX 字段记录，空值/NOASSERTION 不作推断，具体依赖和子目录另行核对。','']
    for group in GROUPS:
        items=[r for r in records if r['category']==group]
        lines += [f'## {group}（{len(items)}）','', '| 仓库 | 用途 | 默认分支 | Fork | 最近推送 UTC | 许可证标识 | C500 线索 |', '|---|---|---|---|---|---|---|']
        for r in items:
            lines.append(f"| [{r['name']}]({r['source_url']}) | {r['purpose']} | `{r['default_branch']}` | {'是' if r['fork'] else '否'} | {r['pushed_at']} | {r['license_spdx'] or '未识别'} | {r['c500_assessment']} |")
        lines.append('')
    lines += ['## 逐仓库证据与分支观察','']
    for r in records:
        rm=r['readme']
        lines += [f"### {r['name']}",'',f"- 来源：[{r['source_url']}]({r['source_url']})；归档={r['archived']}，禁用={r['disabled']}。"]
        if rm['status']=='downloaded':
            lines += [f"- [README 快照]({rm['path']}) · [采集来源]({rm['source_url']})；分支 `{rm['branch']}`；commit `{rm.get('commit') or '未固定，已保存文本 SHA256'}`。"]
        else: lines += ['- 常见根 README 未取得；不代表仓库无其他文档。']
        if r['review_note']:lines += ['- 核对事项：'+r['review_note']]
        if r['c500_clues']:lines += ['- 原文候选行：'+', '.join(str(x['line']) for x in r['c500_clues'])+'（查看完整上下文，不作自动兼容结论）。']
        for key,label in [('branch_observations','分支'),('release_observations','Release')]:
            obs=r[key]
            if obs is None: continue
            if 'error'in obs:lines += [f'- {label}采集失败：'+obs['error']];continue
            names=[b['name'] if key=='branch_observations' else b['tag_name'] for b in obs['data']]
            lines += [f'- [{label} API]({obs["url"]})：'+('、'.join(f'`{n}`' for n in names) or '本次返回空列表')+'。']
        lines.append('')
    (ROOT/'CATALOG.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'repositories':len(records),'groups':dict(collections.Counter(r['category'] for r in records)),
                      'forks':sum(r['fork'] for r in records),'archived':sum(r['archived'] for r in records)},ensure_ascii=False))


if __name__=='__main__':main()
