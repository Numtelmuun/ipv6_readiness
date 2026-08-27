def generate_recommendations(findings, device):
    """Keep the legacy list, but derive every entry from deterministic remediation."""
    severity = {"UPGRADE": "HIGH", "REPLACE": "HIGH", "UPGRADE_OR_REPLACE": "HIGH",
                "CONFIGURE": "MEDIUM", "VERIFY": "LOW"}
    text = {"CONFIGURE": "Configure the required IPv6 state described by this finding.",
            "VERIFY": "Collect or verify the evidence required to resolve this finding.",
            "UPGRADE": "Upgrade the device software as established by deterministic evidence.",
            "REPLACE": "Replace the platform as established by deterministic evidence.",
            "UPGRADE_OR_REPLACE": "Determine whether an OS upgrade is sufficient; otherwise replace the platform."}
    return [{"id": f["id"], "severity": severity[f["remediation"]],
             "remediation": f["remediation"], "recommendation": text[f["remediation"]]}
            for f in findings if f.get("remediation") != "NONE" and f["status"] != "NOT_APPLICABLE"]
