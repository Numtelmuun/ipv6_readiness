from network.inventory import load_devices
from assessment.engine import assess_ipv6
from assessment.summary import summarize_findings


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

    result["summary"] = summarize_findings(
        result["findings"]
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

    total_score = 0.0
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

        total_score += result.get("score", 0.0)

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
        total_score / len(results)
        if results
        else 0.0
    )

    return {
        "summary": summary,
        "average_score": round(
            average_score,
            2
        ),
        "recommendation_count": len(
            recommendations
        ),
        "recommendations": recommendations,
        "devices": [
            {
                "device": result.get("device"),
                "role": result.get("role"),
                "vendor": result.get("vendor"),
                "model": result.get("model"),
                "score": result.get("score"),
                "readiness": result.get("readiness"),
            }
            for result in results
        ],
    }