from network.inventory import load_devices
from assessment.engine import assess_ipv6
from assessment.summary import summarize_findings


ASSESSMENT_PAYLOAD_VERSION = "3.0"

READINESS_PRIORITY = {
    "INSUFFICIENT_DATA": 0,
    "NOT_READY": 1,
    "PARTIALLY_READY": 2,
    "MOSTLY_READY": 3,
    "READY": 4,
}


def aggregate_readiness(results: list[dict]) -> str:
    """Return the least-ready deterministic device state."""

    states = [
        result.get("readiness")
        for result in results
        if result.get("readiness") in READINESS_PRIORITY
    ]
    if not states:
        return "INSUFFICIENT_DATA"
    return min(states, key=READINESS_PRIORITY.__getitem__)


def serialize_device_data(device):
    """Return collected/normalized data without transport credentials."""

    return {
        "hostname": device.hostname,
        "vendor": device.vendor,
        "model": device.model,
        "os_version": device.os_version,
        "role": device.role,
        "platform": device.platform,
        "device_type": device.device_type,
        "required_routing_protocols": list(device.required_routing_protocols),
        "ipv6_supported": device.ipv6_supported,
        "ipv6_routing_enabled": device.ipv6_routing_enabled,
        "interfaces": [
            {
                "name": interface.name,
                "operational": interface.operational,
                "ipv6_enabled": interface.ipv6_enabled,
                "link_local": interface.link_local,
                "global_addresses": interface.global_addresses,
                "prefix_lengths": interface.prefix_lengths,
                "router_advertisements": interface.router_advertisements,
                "dad_enabled": interface.dad_enabled,
            }
            for interface in device.interfaces
        ],
        "routing": {
            "enabled": device.routing.enabled,
            "route_count": device.routing.route_count,
            "connected_routes": device.routing.connected_routes,
            "local_routes": device.routing.local_routes,
            "static_routes": device.routing.static_routes,
            "ospfv3": device.routing.ospfv3,
            "ripng": device.routing.ripng,
            "eigrpv6": device.routing.eigrpv6,
            "bgp_ipv6": device.routing.bgp_ipv6,
            "ipv4_protocols": device.routing.ipv4_protocols,
            "ipv6_protocols": device.routing.ipv6_protocols,
        },
    }


def assess_device(device_name: str):

    devices = load_devices()

    device = next(
        (
            item
            for item in devices
            if item.name == device_name
        ),
        None,
    )

    if device is None:
        raise ValueError(
            f"Device '{device_name}' not found in inventory."
        )

    # ---------------------------------------------
    # Vendor-specific commands come from adapter
    # ---------------------------------------------

    commands = device.adapter.get_commands()

    # ---------------------------------------------
    # Execute commands through network abstraction
    # ---------------------------------------------

    outputs = device.execute_many(commands)

    # ---------------------------------------------
    # Parse using vendor adapter
    # ---------------------------------------------

    normalized = device.adapter.parse_outputs(outputs)

    # ---------------------------------------------
    # Common fields
    # ---------------------------------------------

    normalized.hostname = (
        device.adapter.parse_hostname(outputs)
        or device.name
    )

    normalized.role = device.role
    normalized.platform = device.platform

    # ---------------------------------------------
    # Common IPv6 assessment engine
    # ---------------------------------------------

    result = assess_ipv6(normalized)
    result["device_data"] = serialize_device_data(normalized)

    return result

def assess_all_devices():

    devices = load_devices()

    results = []

    for device in devices:
        result = assess_device(device.name)
        results.append(result)

    summary = {
        "total_devices": len(results),
        "ready": 0,
        "mostly_ready": 0,
        "partially_ready": 0,
        "not_ready": 0,
        "insufficient_data": 0,
    }

    scored_results = []
    recommendations = []

    for result in results:

        readiness = result.get("readiness")

        if readiness == "READY":
            summary["ready"] += 1

        elif readiness == "MOSTLY_READY":
            summary["mostly_ready"] += 1

        elif readiness == "PARTIALLY_READY":
            summary["partially_ready"] += 1

        elif readiness == "NOT_READY":
            summary["not_ready"] += 1

        elif readiness == "INSUFFICIENT_DATA":
            summary["insufficient_data"] += 1

        score = result.get("score")
        if isinstance(score, (int, float)):
            scored_results.append(score)

        for recommendation in result.get(
            "recommendations",
            []
        ):
            recommendations.append(
                {
                    "device": result.get("device"),
                    "role": result.get("role"),
                    **recommendation,
                }
            )

    average_score = (
        round(sum(scored_results) / len(scored_results), 2)
        if scored_results
        else None
    )

    return {
        "summary": summary,
        "average_score": average_score,
        "readiness": aggregate_readiness(results),
        "recommendation_count": len(
            recommendations
        ),
        "recommendations": recommendations,
        "devices": results,
    }


def build_ai_assessment_payload(
    assessment: dict,
    network_name: str = "IPv6 Readiness Assessment",
) -> dict:
    """Create the stable, credential-free input contract for AI inference.

    Raw normalized device data and deterministic assessment findings remain
    separate so an AI consumer can distinguish collected facts from rules.
    """

    devices = []

    for result in assessment.get("devices", []):
        deterministic_assessment = {
            key: result.get(key)
            for key in (
                "device",
                "vendor",
                "model",
                "os_version",
                "role",
                "platform",
                "device_type",
                "required_routing_protocols",
                "score",
                "readiness",
                "summary",
                "findings",
                "recommendations",
            )
        }
        devices.append(
            {
                "device_data": result.get("device_data", {}),
                "deterministic_assessment": deterministic_assessment,
            }
        )

    return {
        "schema_version": ASSESSMENT_PAYLOAD_VERSION,
        "network_name": network_name,
        "aggregate_assessment": {
            "source_of_truth": {
                "score": assessment.get("average_score"),
                "readiness": assessment.get(
                    "readiness",
                    aggregate_readiness(assessment.get("devices", [])),
                ),
                "provenance": "deterministic_assessment_engine",
                "immutable": True,
            },
            "summary": assessment.get("summary", {}),
            "average_score": assessment.get("average_score"),
            "recommendation_count": assessment.get("recommendation_count", 0),
            "recommendations": assessment.get("recommendations", []),
        },
        "ai_interpretation_contract": {
            "deterministic_fields": [
                "aggregate_assessment.source_of_truth.score",
                "aggregate_assessment.source_of_truth.readiness",
                "devices[].deterministic_assessment.score",
                "devices[].deterministic_assessment.readiness",
            ],
            "instructions": [
                "Return interpretation only; never return, copy, recalculate, or reinterpret deterministic identity, score, or readiness fields.",
                "Identify each device analysis only by its exact deterministic device or hostname value so local composition can match it safely.",
                "Do not return vendor, model, platform, device_type, role, score, or readiness in a device analysis.",
                "Do not warn about or recommend adding any absent routing protocol unless required_routing_protocols explicitly marks it required.",
                "Never recommend a routing protocol merely because it is absent.",
                "Do not recommend enabling IPv6 on unspecified or remaining interfaces unless deterministic findings identify those interfaces as requiring IPv6.",
                "Absence of an assessed addressing plan is unknown, not evidence that a plan is missing; recommend validating or reviewing the IPv6 addressing plan when the plan itself was not assessed, never developing one on that basis alone.",
                "Label generic security, transition, routing, and replacement guidance as best_practice unless a deterministic finding supports it as a detected_deficiency, and include the supporting finding IDs for every detected_deficiency.",
                "Preserve unknown values as unknown; do not infer or fill them.",
            ],
        },
        "devices": devices,
    }


def build_final_assessment_report(
    assessment_payload: dict,
    ai_report: dict,
) -> dict:
    """Combine immutable deterministic results with separate AI commentary.

    Identity, score, and readiness are copied only from the deterministic
    payload. AI device entries are matched by device/hostname, and unrecognized
    entries are ignored.
    """

    source = assessment_payload["aggregate_assessment"]["source_of_truth"]
    payload_devices = assessment_payload.get("devices", [])
    deterministic_devices = [
        device.get("deterministic_assessment", {})
        for device in payload_devices
    ]
    deterministic = {
        "score": source.get("score"),
        "readiness": source.get("readiness"),
        "provenance": source.get("provenance"),
        "summary": assessment_payload["aggregate_assessment"].get("summary", {}),
        "recommendations": assessment_payload["aggregate_assessment"].get(
            "recommendations", []
        ),
        "devices": deterministic_devices,
    }

    ai_device_entries = {}
    for item in ai_report.get("device_assessments", []):
        identifier = item.get("device", item.get("hostname"))
        if isinstance(identifier, str) and identifier not in ai_device_entries:
            ai_device_entries[identifier] = item

    deterministic_device_fields = {
        "device",
        "hostname",
        "vendor",
        "model",
        "os_version",
        "platform",
        "device_type",
        "role",
        "score",
        "readiness",
        "deterministic_score",
        "deterministic_readiness",
    }
    device_assessments = []
    for source_entry, device in zip(payload_devices, deterministic_devices):
        device_name = device.get("device")
        hostname = source_entry.get("device_data", {}).get(
            "hostname", device_name
        )
        ai_device = ai_device_entries.get(device_name)
        if ai_device is None:
            ai_device = ai_device_entries.get(hostname, {})
        interpretation = {
            key: value
            for key, value in ai_device.items()
            if key not in deterministic_device_fields
        }
        device_assessments.append(
            {
                "device": device_name,
                "hostname": hostname,
                "vendor": device.get("vendor"),
                "model": device.get("model"),
                "platform": device.get("platform"),
                "device_type": device.get("device_type", "unknown"),
                "role": device.get("role"),
                "deterministic_score": device.get("score"),
                "deterministic_readiness": device.get("readiness"),
                "ai_analysis": interpretation,
            }
        )

    ai_analysis = {
        key: value
        for key, value in ai_report.items()
        if key
        not in {"overall_score", "overall_readiness", "device_assessments"}
    }
    return {
        "schema_version": ASSESSMENT_PAYLOAD_VERSION,
        "network_name": assessment_payload.get("network_name"),
        "deterministic_assessment": deterministic,
        "ai_analysis": ai_analysis,
        "device_assessments": device_assessments,
    }
