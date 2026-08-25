import pytest

from models.ai_report import AIReport, AIReportValidationError


def valid_report():
    return {
        "overall_readiness": "PARTIALLY_READY",
        "overall_score": 55,
        "executive_summary": "Deterministic findings require remediation.",
        "critical_issues": [],
        "device_assessments": [{"device": "R1", "basis": "IPV6-01"}],
        "configuration_recommendations": [],
        "routing_recommendations": [],
        "transition_recommendations": [],
        "device_replacements": [],
        "migration_priorities": [],
        "risks": [],
        "next_steps": [],
    }


def test_ai_report_schema_round_trip():
    report = AIReport.from_dict(valid_report())

    assert report.overall_score == 55.0
    assert report.to_dict()["device_assessments"][0]["device"] == "R1"


def test_ai_report_rejects_invalid_readiness_and_list_shape():
    payload = valid_report()
    payload["overall_readiness"] = "MAYBE"
    with pytest.raises(AIReportValidationError):
        AIReport.from_dict(payload)

    payload = valid_report()
    payload["risks"] = ["not an object"]
    with pytest.raises(AIReportValidationError):
        AIReport.from_dict(payload)


def test_ai_report_rejects_invalid_json():
    with pytest.raises(AIReportValidationError):
        AIReport.from_json("not json")
