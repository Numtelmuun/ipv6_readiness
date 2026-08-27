import json
from copy import deepcopy
from types import SimpleNamespace

from assessment.engine import assess_ipv6
from assessment.service import (
    build_ai_assessment_payload,
    build_final_assessment_report,
)
from mcp_client import decode_tool_content
from models.device import DeviceInfo, IPv6Routing


def unknown_device_result():
    device = DeviceInfo(
        hostname="UNKNOWN-R1",
        vendor="Cisco",
        model="Unknown",
        os_version="Unknown",
        role="core",
        platform="cisco_ios",
        device_type="router",
        ipv6_routing_enabled=None,
        interfaces=[],
        routing=IPv6Routing(enabled=None),
    )
    result = assess_ipv6(device)
    result["device_data"] = {
        "hostname": "UNKNOWN-R1",
        "interfaces": [],
        "ipv6_routing_enabled": None,
    }
    return result


def test_payload_is_json_serializable_and_includes_every_finding():
    result = unknown_device_result()
    second_result = deepcopy(result)
    second_result["device"] = "UNKNOWN-R2"
    second_result["device_data"]["hostname"] = "UNKNOWN-R2"
    aggregate = {
        "summary": {"total_devices": 2, "insufficient_data": 2},
        "average_score": None,
        "recommendation_count": len(result["recommendations"]),
        "recommendations": result["recommendations"],
        "devices": [result, second_result],
    }

    payload = build_ai_assessment_payload(aggregate, "Lab Network")
    encoded = json.dumps(payload)

    assert encoded
    assert payload["network_name"] == "Lab Network"
    assert payload["schema_version"] == "3.0"
    assert payload["aggregate_assessment"]["source_of_truth"] == {
        "score": None,
        "readiness": "INSUFFICIENT_DATA",
        "provenance": "deterministic_assessment_engine",
        "immutable": True,
    }
    assert len(payload["devices"]) == 2
    for device in payload["devices"]:
        assert device["device_data"]["ipv6_routing_enabled"] is None
        deterministic = device["deterministic_assessment"]
        assert deterministic["vendor"] == "Cisco"
        assert deterministic["model"] == "Unknown"
        assert deterministic["platform"] == "cisco_ios"
        assert deterministic["device_type"] == "router"
        assert len(device["deterministic_assessment"]["findings"]) == 9
        assert any(
            finding["status"] == "UNKNOWN"
            for finding in device["deterministic_assessment"]["findings"]
        )


def test_absent_optional_routing_protocols_create_no_recommendations():
    result = unknown_device_result()

    assert "recommendations" in result
    assert not any(
        item["id"] in {"IPV6-05", "IPV6-06", "IPV6-07", "IPV6-08"}
        for item in result["recommendations"]
    )
    routing_findings = {
        finding["id"]: finding
        for finding in result["findings"]
        if finding["id"] in {"IPV6-05", "IPV6-06", "IPV6-07", "IPV6-08"}
    }
    assert all(
        finding["status"] == "NOT_APPLICABLE"
        for finding in routing_findings.values()
    )


def test_explicitly_required_absent_protocol_is_warning_and_recommendation():
    device = DeviceInfo(
        hostname="CORE-R1",
        vendor="Cisco",
        model="CSR1000V",
        role="core",
        platform="cisco_ios",
        device_type="router",
        required_routing_protocols=["BGP IPv6"],
        ipv6_routing_enabled=True,
        routing=IPv6Routing(enabled=True),
    )

    result = assess_ipv6(device)
    bgp = next(item for item in result["findings"] if item["id"] == "IPV6-07")
    assert bgp["status"] == "WARNING"
    assert any(item["id"] == "IPV6-07" for item in result["recommendations"])


def test_present_protocol_does_not_hide_a_different_required_protocol():
    device = DeviceInfo(
        hostname="CORE-R2",
        required_routing_protocols=["RIPng"],
        ipv6_routing_enabled=True,
        routing=IPv6Routing(enabled=True, eigrpv6=True),
    )

    result = assess_ipv6(device)
    other = next(item for item in result["findings"] if item["id"] == "IPV6-08")
    assert other["status"] == "WARNING"
    assert "ripng" in other["message"]


def test_mcp_client_preserves_multiple_content_blocks():
    content = [
        SimpleNamespace(text='{"name": "R1"}'),
        SimpleNamespace(text='{"name": "R3"}'),
    ]

    assert decode_tool_content(content) == [{"name": "R1"}, {"name": "R3"}]


def test_llm_output_without_platform_produces_valid_final_report():
    result = unknown_device_result()
    aggregate = {
        "summary": {"total_devices": 1, "insufficient_data": 1},
        "average_score": None,
        "readiness": "INSUFFICIENT_DATA",
        "recommendations": [],
        "devices": [result],
    }
    payload = build_ai_assessment_payload(aggregate, "Lab Network")
    ai_output = {
        "executive_summary": "Interpretation only.",
        "risks": [],
        "device_assessments": [{
            "device": "UNKNOWN-R1",
            "key_findings": ["Collected data is incomplete."],
        }],
    }

    report = build_final_assessment_report(payload, ai_output)

    assert set(report) == {
        "schema_version",
        "network_name",
        "deterministic_assessment",
        "ai_analysis",
        "device_assessments",
    }
    assert report["deterministic_assessment"]["score"] is None
    assert report["deterministic_assessment"]["readiness"] == "INSUFFICIENT_DATA"
    assert report["ai_analysis"]["executive_summary"] == "Interpretation only."
    assert report["device_assessments"][0]["platform"] == "cisco_ios"
    assert report["device_assessments"][0]["ai_analysis"] == {
        "key_findings": ["Collected data is incomplete."]
    }


def test_ai_contract_guards_against_unsupported_recommendations():
    result = unknown_device_result()
    payload = build_ai_assessment_payload({"devices": [result]})
    instructions = " ".join(payload["ai_interpretation_contract"]["instructions"])

    assert "unspecified or remaining interfaces" in instructions
    assert "validating or reviewing the IPv6 addressing plan" in instructions
    assert "best_practice" in instructions
    assert "Preserve unknown values as unknown" in instructions


def test_llm_cannot_overwrite_deterministic_identity_or_readiness():
    result = unknown_device_result()
    result.update({
        "vendor": "Cisco",
        "model": "CSR1000V",
        "platform": "cisco_ios",
        "device_type": "router",
        "role": "core",
        "score": 42,
        "readiness": "PARTIALLY_READY",
    })
    payload = build_ai_assessment_payload({
        "average_score": 42,
        "readiness": "PARTIALLY_READY",
        "devices": [result],
    })
    report = build_final_assessment_report(payload, {
        "device_assessments": [{
            "device": "UNKNOWN-R1",
            "vendor": "Untrusted Vendor",
            "model": "Untrusted Model",
            "platform": "untrusted_platform",
            "device_type": "firewall",
            "role": "edge",
            "score": 100,
            "readiness": "READY",
            "interpretation": "AI commentary.",
        }],
    })

    device = report["device_assessments"][0]
    assert device["vendor"] == "Cisco"
    assert device["model"] == "CSR1000V"
    assert device["platform"] == "cisco_ios"
    assert device["device_type"] == "router"
    assert device["role"] == "core"
    assert device["deterministic_score"] == 42
    assert device["deterministic_readiness"] == "PARTIALLY_READY"
    assert device["ai_analysis"] == {"interpretation": "AI commentary."}


def test_missing_ai_device_preserves_deterministic_device_with_empty_analysis():
    result = unknown_device_result()
    payload = build_ai_assessment_payload({"devices": [result]})

    report = build_final_assessment_report(payload, {"device_assessments": []})

    assert len(report["device_assessments"]) == 1
    assert report["device_assessments"][0]["device"] == "UNKNOWN-R1"
    assert report["device_assessments"][0]["ai_analysis"] == {}


def test_unknown_ai_device_is_ignored_safely():
    result = unknown_device_result()
    payload = build_ai_assessment_payload({"devices": [result]})

    report = build_final_assessment_report(payload, {
        "device_assessments": [{
            "device": "INVENTED-R99",
            "interpretation": "Unsupported device.",
        }],
    })

    assert len(report["device_assessments"]) == 1
    assert report["device_assessments"][0]["device"] == "UNKNOWN-R1"
    assert report["device_assessments"][0]["ai_analysis"] == {}
