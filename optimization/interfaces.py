"""Planned stage-four boundaries, not runnable backends or vendor APIs.

Reuse the existing CodeOptimizationBackend and IndependentValidator protocols
in contracts.interfaces. Implementations must supply isolation and evidence;
these Protocol declarations do not enforce them.
"""
from typing import Protocol
from contracts.interfaces import Document, OptimizationTask, CandidateBundle, AcceptanceReport


class TaskBuilder(Protocol):
    # Requires completed experiments and actual code callsites, not AnalysisReport alone.
    def build(self, experiment: Document, frozen_scope: Document) -> OptimizationTask: ...


class ConfigProposer(Protocol):
    # Restrict changes to the Study search space; retain parent and effective configuration.
    def propose(self, scope: Document, history: list[Document]) -> list[Document]: ...


class CandidateCollector(Protocol):
    # Preserve development claims; every collected candidate starts unverified.
    def collect(self, task: OptimizationTask, workspace: str) -> CandidateBundle: ...


class AcceptanceCoordinator(Protocol):
    # Dispatch independent validation, including fixed-point model-level retests.
    def evaluate(self, task: OptimizationTask, candidate: CandidateBundle) -> AcceptanceReport: ...


class RollbackExecutor(Protocol):
    # Revert only owned changes/resources; retain evidence of failed attempts.
    def restore(self, parent: Document, owned_resources: Document) -> Document: ...
