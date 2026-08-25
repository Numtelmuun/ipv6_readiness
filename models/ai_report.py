"""Validated, JSON-serializable result contract for Bedrock IPv6 analysis."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from typing import Any


class AIReportValidationError(ValueError):
    """Raised when an AI response does not satisfy the report contract."""


JSON_OBJECT_LIST_FIELDS = (
    "critical_issues",
    "device_assessments",
    "configuration_recommendations",
    "routing_recommendations",
    "transition_recommendations",
    "device_replacements",
    "migration_priorities",
    "risks",
    "next_steps",
)

ALLOWED_READINESS = {
    "READY",
    "PARTIALLY_READY",
    "NOT_READY",
    "INSUFFICIENT_DATA",
}


def _object_list(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise AIReportValidationError(f"{field_name} must be a JSON array.")

    if not all(isinstance(item, dict) for item in value):
        raise AIReportValidationError(
            f"{field_name} entries must be JSON objects."
        )

    return value


@dataclass(frozen=True)
class AIReport:
    overall_readiness: str
    overall_score: float | None
    executive_summary: str
    critical_issues: list[dict[str, Any]]
    device_assessments: list[dict[str, Any]]
    configuration_recommendations: list[dict[str, Any]]
    routing_recommendations: list[dict[str, Any]]
    transition_recommendations: list[dict[str, Any]]
    device_replacements: list[dict[str, Any]]
    migration_priorities: list[dict[str, Any]]
    risks: list[dict[str, Any]]
    next_steps: list[dict[str, Any]]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AIReport":
        if not isinstance(data, dict):
            raise AIReportValidationError("AI response must be a JSON object.")

        required = {
            "overall_readiness",
            "overall_score",
            "executive_summary",
            *JSON_OBJECT_LIST_FIELDS,
        }
        missing = sorted(required - data.keys())
        if missing:
            raise AIReportValidationError(
                "AI response is missing required field(s): " + ", ".join(missing)
            )

        readiness = data["overall_readiness"]
        if readiness not in ALLOWED_READINESS:
            raise AIReportValidationError(
                "overall_readiness must be one of: "
                + ", ".join(sorted(ALLOWED_READINESS))
            )

        score = data["overall_score"]
        if score is not None and (
            not isinstance(score, (int, float))
            or isinstance(score, bool)
            or not 0 <= score <= 100
        ):
            raise AIReportValidationError(
                "overall_score must be a number from 0 to 100 or null."
            )

        summary = data["executive_summary"]
        if not isinstance(summary, str):
            raise AIReportValidationError("executive_summary must be a string.")

        lists = {
            field_name: _object_list(data[field_name], field_name)
            for field_name in JSON_OBJECT_LIST_FIELDS
        }

        return cls(
            overall_readiness=readiness,
            overall_score=float(score) if score is not None else None,
            executive_summary=summary,
            **lists,
        )

    @classmethod
    def from_json(cls, value: str) -> "AIReport":
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as error:
            raise AIReportValidationError("AI response is not valid JSON.") from error

        return cls.from_dict(parsed)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
