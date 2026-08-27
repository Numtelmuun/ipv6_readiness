from models.device import DeviceInfo
from assessment.summary import summarize_findings
from assessment.recommendations import generate_recommendations
from assessment.rules import CHECKLIST_RULES

CHECKLIST_METADATA = {"name": "IPv6 Readiness Checklist", "version": "1.0",
                      "basis": "RIPE-772",
                      "scope": "Basic IPv6 deployment capability and configuration readiness",
                      "full_ripe_772_compliance": False}


def classify_readiness(findings):
    failed = [f for f in findings if f["status"] == "FAIL"]
    remediation = {f["remediation"] for f in failed}
    if "REPLACE" in remediation:
        return "REPLACEMENT_REQUIRED"
    if "UPGRADE" in remediation:
        return "UPGRADE_REQUIRED"
    if "UPGRADE_OR_REPLACE" in remediation:
        return "UPGRADE_OR_REPLACE_REQUIRED"
    if any(f["remediation"] == "CONFIGURE" for f in findings
           if f["status"] in {"FAIL", "WARNING"}):
        return "CONFIGURATION_REQUIRED"
    if any(f["status"] == "UNKNOWN" for f in findings):
        return "INSUFFICIENT_DATA"
    applicable = [f for f in findings if f["status"] != "NOT_APPLICABLE"]
    return "READY" if applicable and all(f["status"] == "PASS" for f in applicable) else "INSUFFICIENT_DATA"


def assess_ipv6(device: DeviceInfo):
    findings = [rule(device) for rule in CHECKLIST_RULES]
    scored = [f for f in findings if f["status"] not in {"NOT_APPLICABLE", "UNKNOWN"}]
    score = None
    if not any(f["status"] == "UNKNOWN" for f in findings) and scored:
        maximum = sum(f["max_score"] for f in scored)
        score = round(sum(f["score"] for f in scored) / maximum * 100, 2) if maximum else None
    return {
        "checklist": dict(CHECKLIST_METADATA), "device": device.hostname, "vendor": device.vendor,
        "model": device.model, "os_version": device.os_version, "role": device.role,
        "platform": device.platform, "device_type": device.device_type,
        "required_routing_protocols": list(device.required_routing_protocols),
        "required_ipv6_interfaces": (None if device.required_ipv6_interfaces is None
                                     else list(device.required_ipv6_interfaces)),
        "score": score, "readiness": classify_readiness(findings),
        "summary": summarize_findings(findings), "findings": findings,
        "recommendations": generate_recommendations(findings, device),
    }
