import pytest

from models.ai_report import AIReport, AIReportValidationError


def valid_report():
    return {
        "executive_summary": "Deterministic findings require remediation.",
        "critical_issues": [],
        "device_assessments": [{
            "device": "R1",
            "key_findings": ["IPv6 is enabled."],
        }],
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

    assert report.to_dict()["device_assessments"][0]["device"] == "R1"


def test_ai_report_rejects_invalid_list_shape():
    payload = valid_report()
    payload["risks"] = ["not an object"]
    with pytest.raises(AIReportValidationError):
        AIReport.from_dict(payload)


def test_ai_report_rejects_invalid_json():
    with pytest.raises(AIReportValidationError):
        AIReport.from_json("not json")


def test_ai_report_requires_only_stable_device_identifier():
    payload = valid_report()
    del payload["device_assessments"][0]["device"]

    with pytest.raises(AIReportValidationError, match="device or hostname"):
        AIReport.from_dict(payload)


def test_ai_report_accepts_hostname_identifier_without_factual_identity():
    payload = valid_report()
    payload["device_assessments"] = [{
        "hostname": "R1",
        "interpretation": "No platform echo is required.",
    }]

    assert AIReport.from_dict(payload).device_assessments[0]["hostname"] == "R1"


def test_recommendations_distinguish_deficiencies_from_best_practices():
    payload = valid_report()
    payload["transition_recommendations"] = [{
        "recommendation_type": "best_practice",
        "recommendation": "Review transition requirements.",
    }]
    assert AIReport.from_dict(payload).transition_recommendations

    payload["transition_recommendations"] = [{
        "recommendation_type": "detected_deficiency",
        "recommendation": "Add a transition mechanism.",
    }]
    with pytest.raises(AIReportValidationError, match="finding_ids"):
        AIReport.from_dict(payload)
