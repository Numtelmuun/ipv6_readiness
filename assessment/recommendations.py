def generate_recommendations(findings, device):

    recommendations = []

    for finding in findings:

        if finding["status"] == "FAIL":

            if finding["id"] == "IPV6-01":
                recommendations.append({
                    "id": finding["id"],
                    "severity": "HIGH",
                    "recommendation": (
                        "Enable IPv6 on the required network interfaces."
                    )
                })

            elif finding["id"] == "IPV6-02":
                recommendations.append({
                    "id": finding["id"],
                    "severity": "HIGH",
                    "recommendation": (
                        "Configure at least one global IPv6 address "
                        "on the required interface."
                    )
                })

            elif finding["id"] == "IPV6-03":
                recommendations.append({
                    "id": finding["id"],
                    "severity": "MEDIUM",
                    "recommendation": (
                        "Configure or verify IPv6 link-local "
                        "addresses on IPv6-enabled interfaces."
                    )
                })

            elif finding["id"] == "IPV6-04":
                recommendations.append({
                    "id": finding["id"],
                    "severity": "HIGH",
                    "recommendation": (
                        "Enable IPv6 unicast routing on the device."
                    )
                })

        elif finding["status"] == "WARNING":

            if finding["id"] == "IPV6-05":
                recommendations.append({
                    "id": finding["id"],
                    "severity": "MEDIUM",
                    "recommendation": (
                        "Configure the IPv6 routing protocol explicitly "
                        "required for this device."
                    )
                })

            elif finding["id"] == "IPV6-07":
                recommendations.append({
                    "id": finding["id"],
                    "severity": "LOW",
                    "recommendation": (
                        "Configure IPv6 BGP because the deterministic "
                        "input explicitly marks it as required."
                    )
                })

            elif finding["id"] == "IPV6-08":
                recommendations.append({
                    "id": finding["id"],
                    "severity": "LOW",
                    "recommendation": (
                        "Configure the RIPng or EIGRPv6 protocol explicitly "
                        "required by the deterministic input."
                    )
                })

    return recommendations
