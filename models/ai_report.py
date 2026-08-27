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

def _object_list(value: Any, field_name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise AIReportValidationError(f"{field_name} must be a JSON array.")

    if not all(isinstance(item, dict) for item in value):
        raise AIReportValidationError(
            f"{field_name} entries must be JSON objects."
        )

    return value


def _validate_device_assessments(items: list[dict[str, Any]]) -> None:
    for index, item in enumerate(items):
        identifier = item.get("device", item.get("hostname"))
        if not isinstance(identifier, str) or not identifier.strip():
            raise AIReportValidationError(
                f"device_assessments[{index}] must include a non-empty "
                "device or hostname identifier."
            )


def _validate_recommendations(
    items: list[dict[str, Any]], field_name: str
) -> None:
    for index, item in enumerate(items):
        recommendation_type = item.get("recommendation_type")
        if recommendation_type not in {"detected_deficiency", "best_practice"}:
            raise AIReportValidationError(
                f"{field_name}[{index}].recommendation_type must be "
                "detected_deficiency or best_practice."
            )
        if recommendation_type == "detected_deficiency" and not item.get(
            "finding_ids"
        ):
            raise AIReportValidationError(
                f"{field_name}[{index}] detected_deficiency must include "
                "finding_ids."
            )


@dataclass(frozen=True)
class AIReport:
    """Interpretive-only Bedrock response prior to deterministic composition."""
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
            "executive_summary",
            *JSON_OBJECT_LIST_FIELDS,
        }
        missing = sorted(required - data.keys())
        if missing:
            raise AIReportValidationError(
                "AI response is missing required field(s): " + ", ".join(missing)
            )

        summary = data["executive_summary"]
        if not isinstance(summary, str):
            raise AIReportValidationError("executive_summary must be a string.")

        lists = {
            field_name: _object_list(data[field_name], field_name)
            for field_name in JSON_OBJECT_LIST_FIELDS
        }
        _validate_device_assessments(lists["device_assessments"])
        for field_name in (
            "configuration_recommendations",
            "routing_recommendations",
            "transition_recommendations",
            "device_replacements",
        ):
            _validate_recommendations(lists[field_name], field_name)

        return cls(
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
