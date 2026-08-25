import json
from copy import deepcopy
from types import SimpleNamespace

from assessment.engine import assess_ipv6
from assessment.service import build_ai_assessment_payload
from mcp_client import decode_tool_content
from models.device import DeviceInfo, IPv6Routing


def unknown_device_result():
    device = DeviceInfo(
        hostname="UNKNOWN-R1",
        vendor="Cisco",
        model="Unknown",
        os_version="Unknown",
        role="core",
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
    assert len(payload["devices"]) == 2
    for device in payload["devices"]:
        assert device["device_data"]["ipv6_routing_enabled"] is None
        assert len(device["deterministic_assessment"]["findings"]) == 9
        assert any(
            finding["status"] == "UNKNOWN"
            for finding in device["deterministic_assessment"]["findings"]
        )


def test_deterministic_engine_includes_existing_recommendations():
    result = unknown_device_result()

    assert "recommendations" in result
    assert any(item["id"] == "IPV6-05" for item in result["recommendations"])


def test_mcp_client_preserves_multiple_content_blocks():
    content = [
        SimpleNamespace(text='{"name": "R1"}'),
        SimpleNamespace(text='{"name": "R3"}'),
    ]

    assert decode_tool_content(content) == [{"name": "R1"}, {"name": "R3"}]
