def generate_recommendations(findings, device):
    """Keep the legacy list, but derive every entry from deterministic remediation."""
    severity = {"UPGRADE": "HIGH", "REPLACE": "HIGH", "UPGRADE_OR_REPLACE": "HIGH",
                "CONFIGURE": "MEDIUM", "VERIFY": "LOW"}
    text = {"CONFIGURE": "Configure the required IPv6 state described by this finding.",
            "VERIFY": "Collect or verify the evidence required to resolve this finding.",
            "UPGRADE": "Upgrade the device software as established by deterministic evidence.",
            "REPLACE": "Replace the platform as established by deterministic evidence.",
            "UPGRADE_OR_REPLACE": "Determine whether an OS upgrade is sufficient; otherwise replace the platform."}
    recommendations = []
    for finding in findings:
        remediation = finding.get("remediation")
        if remediation == "NONE" or finding["status"] == "NOT_APPLICABLE":
            continue
        recommendation = text[remediation]
        if (finding["id"] == "IPV6-09" and finding["status"] == "WARNING"
                and remediation == "VERIFY"):
            recommendation = "Verify the required interface operational state and link condition."
        recommendations.append({"id": finding["id"], "severity": severity[remediation],
                                "remediation": remediation,
                                "recommendation": recommendation})
    return recommendations
