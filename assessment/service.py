from network.inventory import load_devices
from assessment.engine import assess_ipv6
from assessment.summary import summarize_findings


ASSESSMENT_PAYLOAD_VERSION = "1.0"


def serialize_device_data(device):
    """Return collected/normalized data without transport credentials."""

    return {
        "hostname": device.hostname,
        "vendor": device.vendor,
        "model": device.model,
        "os_version": device.os_version,
        "role": device.role,
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
            "summary": assessment.get("summary", {}),
            "average_score": assessment.get("average_score"),
            "recommendation_count": assessment.get("recommendation_count", 0),
            "recommendations": assessment.get("recommendations", []),
        },
        "devices": devices,
    }
