"""InferOptLab custom interface design draft for Python 3.11+.

These protocols are a proposed InferOptLab API, not existing KDA, AISim,
vLLM, SGLang, or hardware-vendor APIs. No GPU execution or third-party SDK
is implemented here. Methods contain only ellipses.

Domain objects use read-only mappings of their canonical top-level fields.
The repository's schemas, rather than these aliases, define complete fields
and validation rules. There is no additional id/data wrapper around the YAML
examples. Aliases intentionally do not provide nominal type safety.

Code-optimization backends emit CandidateBundle objects whose
"validation_status" is "unverified". Development measurements and agent
claims do not establish acceptance. An IndependentValidator produces a
separate AcceptanceReport; it does not overwrite development evidence.

Capability "verified" means evidence exists for the recorded environment
and feature scope. It is not a promise of support on another version, model,
device, or deployment. "unverified" is distinct from "unsupported".
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Literal, Protocol, TypeAlias, TypedDict


JSONValue: TypeAlias = (
    None
    | bool
    | int
    | float
    | str
    | list["JSONValue"]
    | dict[str, "JSONValue"]
)


# The schemas retain object-specific IDs such as study_id and task_id.
# Runtime bindings should be generated or contract-tested against them.
Document: TypeAlias = Mapping[str, JSONValue]
StudySpec: TypeAlias = Document
EnvironmentSnapshot: TypeAlias = Document
WorkloadSpec: TypeAlias = Document
DeploymentSpec: TypeAlias = Document
CandidateSpec: TypeAlias = Document
TrialSpec: TypeAlias = Document
RunRecord: TypeAlias = Document
MeasurementBundle: TypeAlias = Document
Hypothesis: TypeAlias = Document
DiagnosisPlan: TypeAlias = Document
DiagnosisReport: TypeAlias = Document
AnalysisMethod: TypeAlias = Document
AnalysisPlan: TypeAlias = Document
AnalysisReport: TypeAlias = Document
TraceCapture: TypeAlias = Document
TraceSummary: TypeAlias = Document
OptimizationTask: TypeAlias = Document
OptimizationHandoff: TypeAlias = Document
CandidateBundle: TypeAlias = Document
AcceptanceReport: TypeAlias = Document
PredictionResult: TypeAlias = Document

# Execution-layer handles are also versioned, serializable documents.
ExecutionPlan: TypeAlias = Document
ResourceLease: TypeAlias = Document
CodeSession: TypeAlias = Document

CapabilityState: TypeAlias = Literal["verified", "unsupported", "unverified"]
CandidateValidationState: TypeAlias = Literal["unverified"]
DEFAULT_CANDIDATE_VALIDATION_STATUS: CandidateValidationState = "unverified"


class ArtifactRef(TypedDict):
    uri: str
    sha256: str
    media_type: str


class CapabilityResult(TypedDict):
    state: CapabilityState
    scope: dict[str, JSONValue]
    evidence: list[ArtifactRef]
    reason: str | None


CapabilityMap: TypeAlias = Mapping[str, CapabilityResult]


class DeviceAdapter(Protocol):
    def inspect(self) -> EnvironmentSnapshot: ...

    def capabilities(self, environment: EnvironmentSnapshot) -> CapabilityMap: ...

    def validate_deployment(
        self,
        deployment: DeploymentSpec,
        environment: EnvironmentSnapshot,
    ) -> CapabilityMap: ...


class FrameworkAdapter(Protocol):
    def capabilities(self, environment: EnvironmentSnapshot) -> CapabilityMap: ...

    def plan_deployment(
        self,
        study: StudySpec,
        deployment: DeploymentSpec,
        environment: EnvironmentSnapshot,
    ) -> ExecutionPlan: ...

    def plan_benchmark(
        self,
        trial: TrialSpec,
        workload: WorkloadSpec,
        environment: EnvironmentSnapshot,
    ) -> ExecutionPlan: ...

    def parse_measurements(
        self,
        run: RunRecord,
        artifacts: Sequence[ArtifactRef],
    ) -> MeasurementBundle: ...


class ModelAdapter(Protocol):
    def inspect_model(
        self,
        study: StudySpec,
        environment: EnvironmentSnapshot,
    ) -> Mapping[str, JSONValue]: ...

    def validate_deployment(
        self,
        study: StudySpec,
        deployment: DeploymentSpec,
        environment: EnvironmentSnapshot,
    ) -> CapabilityMap: ...

    def correctness_requirements(
        self,
        study: StudySpec,
        workload: WorkloadSpec,
    ) -> Mapping[str, JSONValue]: ...


class ProfilerAdapter(Protocol):
    def capabilities(self, environment: EnvironmentSnapshot) -> CapabilityMap: ...

    def plan_capture(
        self,
        trial: TrialSpec,
        environment: EnvironmentSnapshot,
    ) -> ExecutionPlan: ...

    def parse_capture(
        self,
        run: RunRecord,
        artifacts: Sequence[ArtifactRef],
    ) -> MeasurementBundle: ...


class ExecutionBackend(Protocol):
    def acquire_lease(
        self,
        deployment: DeploymentSpec,
        environment: EnvironmentSnapshot,
        *,
        owner_id: str,
        ttl_seconds: int,
    ) -> ResourceLease: ...

    def renew_lease(
        self,
        lease: ResourceLease,
        *,
        ttl_seconds: int,
    ) -> ResourceLease: ...

    def release_lease(self, lease: ResourceLease) -> None: ...

    def submit(
        self,
        trial: TrialSpec,
        plan: ExecutionPlan,
        lease: ResourceLease,
    ) -> RunRecord: ...

    def poll(self, run_id: str) -> RunRecord: ...

    def cancel(self, run_id: str) -> RunRecord: ...

    def collect_artifacts(self, run_id: str) -> Sequence[ArtifactRef]: ...


class ConfigSearchStrategy(Protocol):
    # StudySpec owns objectives, resource limits, allowed search dimensions,
    # and workload identity. History/report retain failed and rejected trials.
    def propose(
        self,
        study: StudySpec,
        history: Sequence[RunRecord],
        report: AcceptanceReport | None,
        *,
        hypotheses: Sequence[Hypothesis] = (),
        limit: int = 1,
    ) -> Sequence[CandidateSpec]: ...


class DiagnosisEngine(Protocol):
    # Offline evidence only. Missing trace or intervention never confirms a cause.
    def diagnose(self, plan: DiagnosisPlan) -> DiagnosisReport: ...


class InvestigationPlanner(Protocol):
    # Planning has no GPU execution side effects; baseline-free tasks stay pending.
    def plan_tasks(self, plan: AnalysisPlan, diagnosis: DiagnosisReport | None) -> AnalysisReport: ...


class TraceNormalizer(Protocol):
    # A future qualified native-format adapter must preserve units and clock domains.
    # Satisfying this protocol alone does not establish vendor-profiler support.
    def normalize(self, artifacts: Sequence[ArtifactRef]) -> TraceCapture: ...


class PerformanceModel(Protocol):
    # Predictions retain predictor/data revisions, coverage and uncertainty.
    # They cannot be promoted to measured results without an actual Run.
    def applicability(
        self,
        study: StudySpec,
        candidate: CandidateSpec,
        environment: EnvironmentSnapshot,
    ) -> CapabilityResult: ...

    def predict(
        self,
        study: StudySpec,
        candidate: CandidateSpec,
        workload: WorkloadSpec,
        environment: EnvironmentSnapshot,
    ) -> PredictionResult: ...


class CodeOptimizationBackend(Protocol):
    # The export contains development inputs and rules only. Hidden acceptance
    # data and writable access to the independent verifier are excluded.
    def export_task(
        self,
        task: OptimizationTask,
        *,
        workspace_uri: str,
    ) -> ArtifactRef: ...

    # The task pins the baseline, edit scope, GPU/time/token budgets, and
    # stop conditions. The execution layer retains authority over the lease.
    def start_session(
        self,
        task: OptimizationTask,
        exported_task: ArtifactRef,
        lease: ResourceLease,
    ) -> CodeSession: ...

    # Every emitted bundle is externally unverified, including candidates
    # whose development tests passed. Preserve code scope and dev_claims.
    def collect_candidates(self, session: CodeSession) -> Sequence[CandidateBundle]: ...

    def stop_session(self, session: CodeSession) -> None: ...


class IndependentValidator(Protocol):
    # Candidate validation verifies the frozen contract, build, correctness,
    # and acceptance evidence. It does not trust agent-reported pass flags.
    def validate_candidate(
        self,
        task: OptimizationTask,
        candidate: CandidateBundle,
        environment: EnvironmentSnapshot,
        lease: ResourceLease,
    ) -> AcceptanceReport: ...

    # End-to-end acceptance remains separate from code/microbenchmark checks.
    def evaluate_trial(
        self,
        study: StudySpec,
        trial: TrialSpec,
        run: RunRecord,
        measurements: MeasurementBundle,
        baseline: MeasurementBundle,
    ) -> AcceptanceReport: ...


class ArtifactStore(Protocol):
    # Implementations return content-addressed references and preserve prior
    # evidence. Metadata must not silently mutate a previously accepted run.
    def put(
        self,
        content: bytes,
        *,
        media_type: str,
        metadata: Mapping[str, JSONValue],
    ) -> ArtifactRef: ...

    def get(self, reference: ArtifactRef) -> bytes: ...

    def exists(self, reference: ArtifactRef) -> bool: ...
