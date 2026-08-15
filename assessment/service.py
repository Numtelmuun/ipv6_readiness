from network.inventory import load_devices

from parsers.cisco_parser import (
    parse_ipv6_device_data,
    parse_hostname,
)

from assessment.engine import assess_ipv6
from assessment.summary import summarize_findings
from assessment.recommendations import generate_recommendations


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

    commands = [
        "show version",
        "show ipv6 interface brief",
        "show ipv6 route",
        "show ipv6 protocols",
        "show running-config | include ^hostname",
    ]

    outputs = device.execute_many(commands)

    version = outputs[
        "show version"
    ]

    interfaces = outputs[
        "show ipv6 interface brief"
    ]

    routing = outputs[
        "show ipv6 route"
    ]

    protocols = outputs[
        "show ipv6 protocols"
    ]

    hostname_output = outputs[
        "show running-config | include ^hostname"
    ]

    normalized = parse_ipv6_device_data(
        version_output=version,
        interface_output=interfaces,
        routing_output=routing,
        protocols_output=protocols,
    )

    normalized.hostname = (
        parse_hostname(hostname_output)
        or device.name
    )

    normalized.role = device.role

    result = assess_ipv6(normalized)

    result["summary"] = summarize_findings(
        result["findings"]
    )

    result["recommendations"] = generate_recommendations(
        result["findings"],
        normalized
    )

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
    }

    total_score = 0

    all_recommendations = []

    for result in results:

        readiness = result["readiness"]

        if readiness == "READY":
            summary["ready"] += 1

        elif readiness == "MOSTLY_READY":
            summary["mostly_ready"] += 1

        elif readiness == "PARTIALLY_READY":
            summary["partially_ready"] += 1

        elif readiness == "NOT_READY":
            summary["not_ready"] += 1

        total_score += result["score"]

        for recommendation in result.get(
            "recommendations",
            []
        ):
            all_recommendations.append({
                "device": result["device"],
                "role": result["role"],
                **recommendation,
            })

    if results:
        average_score = round(
            total_score / len(results),
            2
        )
    else:
        average_score = 0

    return {
        "summary": summary,
        "average_score": average_score,
        "recommendation_count": len(
            all_recommendations
        ),
        "recommendations": all_recommendations,
        "devices": [
            {
                "device": result["device"],
                "role": result["role"],
                "vendor": result["vendor"],
                "model": result["model"],
                "score": result["score"],
                "readiness": result["readiness"],
            }
            for result in results
        ],
    }