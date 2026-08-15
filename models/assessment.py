from dataclasses import dataclass
from typing import Optional


@dataclass
class FindingSummary:
    pass_count: int
    fail_count: int
    warning_count: int
    unknown_count: int
    not_applicable_count: int


@dataclass
class AssessmentResult:
    device: str
    vendor: str
    model: str
    os_version: str
    role: str

    score: Optional[float]
    readiness: str

    summary: FindingSummary
    findings: list