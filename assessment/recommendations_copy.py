def generate_recommendations(findings):

    recommendations = []

    for finding in findings:

        status = finding["status"]
        rule_id = finding["id"]

        if status not in ["FAIL", "WARNING", "UNKNOWN"]:
            continue

        recommendation = None

        # IPV6-01
        if rule_id == "IPV6-01":

            if status == "FAIL":
                recommendation = {
                    "rule": rule_id,
                    "priority": "HIGH",
                    "title": "Enable IPv6 on interfaces",
                    "message": (
                        "Configure IPv6 on the required network "
                        "interfaces."
                    ),
                    "remediation": (
                        "interface <interface>\n"
                        " ipv6 enable"
                    ),
                }

            elif status == "UNKNOWN":
                recommendation = {
                    "rule": rule_id,
                    "priority": "HIGH",
                    "title": "Verify IPv6 interface configuration",
                    "message": (
                        "Interface information could not be "
                        "determined. Verify device access and "
                        "collection output."
                    ),
                    "remediation": (
                        "show ipv6 interface brief"
                    ),
                }

        # IPV6-02
        elif rule_id == "IPV6-02":

            if status == "FAIL":
                recommendation = {
                    "rule": rule_id,
                    "priority": "HIGH",
                    "title": "Configure global IPv6 address",
                    "message": (
                        "Configure at least one appropriate "
                        "global IPv6 address."
                    ),
                    "remediation": (
                        "interface <interface>\n"
                        " ipv6 address <IPv6-address>/<prefix>"
                    ),
                }

            elif status == "UNKNOWN":
                recommendation = {
                    "rule": rule_id,
                    "priority": "HIGH",
                    "title": "Verify IPv6 address information",
                    "message": (
                        "IPv6 interface information could not "
                        "be determined."
                    ),
                    "remediation": (
                        "show ipv6 interface brief"
                    ),
                }

        # IPV6-03
        elif rule_id == "IPV6-03":

            if status == "FAIL":
                recommendation = {
                    "rule": rule_id,
                    "priority": "MEDIUM",
                    "title": "Configure IPv6 link-local address",
                    "message": (
                        "Ensure IPv6-enabled interfaces have "
                        "link-local addresses."
                    ),
                    "remediation": (
                        "interface <interface>\n"
                        " ipv6 enable"
                    ),
                }

            elif status == "UNKNOWN":
                recommendation = {
                    "rule": rule_id,
                    "priority": "MEDIUM",
                    "title": "Verify IPv6 link-local addresses",
                    "message": (
                        "Interface information could not be "
                        "determined."
                    ),
                    "remediation": (
                        "show ipv6 interface brief"
                    ),
                }

        # IPV6-04
        elif rule_id == "IPV6-04":

            if status == "FAIL":
                recommendation = {
                    "rule": rule_id,
                    "priority": "CRITICAL",
                    "title": "Enable IPv6 routing",
                    "message": (
                        "IPv6 routing is disabled on this router."
                    ),
                    "remediation": (
                        "configure terminal\n"
                        " ipv6 unicast-routing"
                    ),
                }

            elif status == "UNKNOWN":
                recommendation = {
                    "rule": rule_id,
                    "priority": "HIGH",
                    "title": "Verify IPv6 routing state",
                    "message": (
                        "IPv6 routing state could not be determined."
                    ),
                    "remediation": (
                        "show running-config | include "
                        "ipv6 unicast-routing"
                    ),
                }

        # IPV6-05
        elif rule_id == "IPV6-05":

            if status == "WARNING":
                recommendation = {
                    "rule": rule_id,
                    "priority": "MEDIUM",
                    "title": "Configure IPv6 dynamic routing",
                    "message": (
                        "No IPv6 dynamic routing protocol was "
                        "detected on this core device."
                    ),
                    "remediation": (
                        "Consider configuring OSPFv3, "
                        "EIGRPv6, RIPng, or IPv6 BGP "
                        "according to the network design."
                    ),
                }

            elif status == "UNKNOWN":
                recommendation = {
                    "rule": rule_id,
                    "priority": "HIGH",
                    "title": "Verify IPv6 routing protocols",
                    "message": (
                        "IPv6 dynamic routing information "
                        "could not be determined."
                    ),
                    "remediation": (
                        "show ipv6 protocols"
                    ),
                }

        # IPV6-06
        elif rule_id == "IPV6-06":

            if status == "WARNING":
                recommendation = {
                    "rule": rule_id,
                    "priority": "MEDIUM",
                    "title": "Consider OSPFv3",
                    "message": (
                        "OSPFv3 was not detected on this core "
                        "router."
                    ),
                    "remediation": (
                        "If OSPFv3 is part of the network design, "
                        "configure an IPv6 OSPFv3 process and "
                        "enable it on the required interfaces."
                    ),
                }

            elif status == "UNKNOWN":
                recommendation = {
                    "rule": rule_id,
                    "priority": "MEDIUM",
                    "title": "Verify OSPFv3 configuration",
                    "message": (
                        "OSPFv3 configuration could not be "
                        "determined."
                    ),
                    "remediation": (
                        "show ipv6 protocols"
                    ),
                }

        # IPV6-07
        elif rule_id == "IPV6-07":

            if status == "WARNING":
                recommendation = {
                    "rule": rule_id,
                    "priority": "LOW",
                    "title": "Review IPv6 BGP requirement",
                    "message": (
                        "IPv6 BGP was not detected."
                    ),
                    "remediation": (
                        "Verify whether IPv6 BGP is required "
                        "by the network architecture."
                    ),
                }

        # IPV6-08
        elif rule_id == "IPV6-08":

            if status == "WARNING":
                recommendation = {
                    "rule": rule_id,
                    "priority": "LOW",
                    "title": "Review alternative IPv6 routing protocols",
                    "message": (
                        "Neither RIPng nor EIGRPv6 was detected."
                    ),
                    "remediation": (
                        "Use the routing protocol required by "
                        "the network design."
                    ),
                }

        # IPV6-09
        elif rule_id == "IPV6-09":

            if status == "WARNING":
                recommendation = {
                    "rule": rule_id,
                    "priority": "MEDIUM",
                    "title": "Configure additional IPv6 interfaces",
                    "message": (
                        "The core router has fewer than two "
                        "IPv6-enabled interfaces."
                    ),
                    "remediation": (
                        "Configure IPv6 on the required "
                        "additional interfaces."
                    ),
                }

            elif status == "UNKNOWN":
                recommendation = {
                    "rule": rule_id,
                    "priority": "MEDIUM",
                    "title": "Verify interface information",
                    "message": (
                        "IPv6 interface information could not "
                        "be determined."
                    ),
                    "remediation": (
                        "show ipv6 interface brief"
                    ),
                }

        if recommendation:
            recommendations.append(recommendation)

    return recommendations