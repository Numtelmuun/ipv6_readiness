def summarize_findings(findings):

    summary = {
        "pass": 0,
        "fail": 0,
        "warning": 0,
        "unknown": 0,
        "not_applicable": 0,
    }

    for finding in findings:

        status = finding["status"]

        if status == "PASS":
            summary["pass"] += 1

        elif status == "FAIL":
            summary["fail"] += 1

        elif status == "WARNING":
            summary["warning"] += 1

        elif status == "UNKNOWN":
            summary["unknown"] += 1

        elif status == "NOT_APPLICABLE":
            summary["not_applicable"] += 1

    return summary