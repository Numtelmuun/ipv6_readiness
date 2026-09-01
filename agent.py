"""Local orchestration entry point for deterministic and Bedrock AI reports."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from assessment.service import (
    build_ai_assessment_payload,
    build_final_assessment_report,
)
from aws_ai.bedrock_client import BedrockIPv6Client
from mcp_client import call_tool


async def assess_network() -> dict:
    """Run the existing local deterministic MCP assessment."""
    return await call_tool("assess_all_ipv6_devices", {})


async def build_assessment_payload(network_name: str) -> dict:
    """Build AI input locally after deterministic collection completes."""
    assessment = await assess_network()
    return build_ai_assessment_payload(assessment, network_name=network_name)


async def run_ai_assessment(network_name: str) -> dict:
    """Send only the completed credential-free assessment to Bedrock."""
    payload = await build_assessment_payload(network_name)
    ai_report = BedrockIPv6Client().assess(payload).to_dict()
    return build_final_assessment_report(payload, ai_report)


def generate_report(data: dict) -> None:
    """Display the deterministic assessment without requiring AWS."""
    summary = data["summary"]
    average = data["average_score"]
    average_text = "N/A" if average is None else f"{average}%"

    print("\n" + "=" * 60)
    print("IPv6 READINESS REPORT (DETERMINISTIC)")
    print("=" * 60)
    print(f"\nTotal devices: {summary['total_devices']}")
    print(f"Average score: {average_text}")
    print("\nReadiness:")
    for status, key in (
        ("READY", "ready"),
        ("CONFIGURATION_REQUIRED", "configuration_required"),
        ("UPGRADE_REQUIRED", "upgrade_required"),
        ("REPLACEMENT_REQUIRED", "replacement_required"),
        ("UPGRADE_OR_REPLACE_REQUIRED", "upgrade_or_replace_required"),
        ("INSUFFICIENT_DATA", "insufficient_data"),
    ):
        print(f"  {status:28} {summary.get(key, 0)}")

    print("\nDevices:")
    for device in data["devices"]:
        score = device.get("score")
        score_text = "N/A" if score is None else f"{score}%"
        print(
            f"  {device.get('device', 'UNKNOWN'):12} "
            f"{device.get('role', 'UNKNOWN'):8} "
            f"{score_text:8} {device.get('readiness', 'UNKNOWN')}"
        )

    print("\nDeterministic recommendations:")
    recommendations = data.get("recommendations", [])
    if not recommendations:
        print("  No recommendations.")
    for recommendation in recommendations:
        print(
            f"  [{recommendation['severity']}] "
            f"{recommendation['device']} - {recommendation['id']}: "
            f"{recommendation['recommendation']}"
        )


def display_ai_report(report: dict) -> None:
    print("\n" + "=" * 60)
    print("IPv6 READINESS REPORT (AWS BEDROCK AI ANALYSIS)")
    print("=" * 60)
    print(json.dumps(report, ensure_ascii=False, indent=2))


def save_json(value: dict, output_path: str | None) -> None:
    if output_path:
        Path(output_path).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


async def run_cli(force_ai: bool = False) -> None:
    parser = argparse.ArgumentParser(description="Local IPv6 readiness workflow")
    parser.add_argument("--ai", action="store_true", help="Use AWS Bedrock.")
    parser.add_argument(
        "--network-name",
        default="IPv6 Readiness Assessment",
        help="Network name included in the AI input payload.",
    )
    parser.add_argument("--output", help="Optional path for resulting JSON.")
    args = parser.parse_args()

    if args.ai or force_ai:
        report = await run_ai_assessment(args.network_name)
        display_ai_report(report)
        save_json(report, args.output)
        return

    assessment = await assess_network()
    generate_report(assessment)
    save_json(assessment, args.output)


if __name__ == "__main__":
    asyncio.run(run_cli())
