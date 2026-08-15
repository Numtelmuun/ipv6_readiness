from models.device import DeviceInfo
from assessment.summary import summarize_findings
from assessment.rules import (
    check_ipv6_interfaces,
    check_global_ipv6_address,
    check_link_local,
    check_ipv6_routing,
    check_dynamic_routing,
    check_ospfv3,
    check_bgp_ipv6,
    check_other_dynamic_routing,
    check_multiple_ipv6_interfaces,
)


def assess_ipv6(device: DeviceInfo):

    rules = [
        check_ipv6_interfaces,
        check_global_ipv6_address,
        check_link_local,
        check_ipv6_routing,
        check_dynamic_routing,
        check_ospfv3,
        check_bgp_ipv6,
        check_other_dynamic_routing,
        check_multiple_ipv6_interfaces,
    ]

    findings = []

    total_score = 0
    maximum_score = 0

    for rule in rules:

        result = rule(device)

        findings.append(result)

        if result["status"] in [
            "NOT_APPLICABLE",
            "UNKNOWN",
        ]:
            continue

        total_score += result["score"]
        maximum_score += result["max_score"]
        unknown_count = sum(
    1
    for finding in findings
    if finding["status"] == "UNKNOWN"
)
    if unknown_count > 0:
        score = None
        readiness = "INSUFFICIENT_DATA"

    elif maximum_score > 0:
        score = round(
            (total_score / maximum_score) * 100,
            2
        )

        if score >= 85:
            readiness = "READY"

        elif score >= 65:
            readiness = "MOSTLY_READY"

        elif score >= 40:
            readiness = "PARTIALLY_READY"

        else:
            readiness = "NOT_READY"

    else:
        score = None
        readiness = "INSUFFICIENT_DATA"
    return {
        "device": device.hostname,
        "vendor": device.vendor,
        "model": device.model,
        "os_version": device.os_version,
        "role": device.role,
        "score": score,
        "readiness": readiness,
        "summary": summarize_findings(findings),
        "findings": findings,
    }