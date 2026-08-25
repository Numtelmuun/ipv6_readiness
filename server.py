from mcp.server.mcpserver import MCPServer

from assessment.service import (
    assess_device,
    assess_all_devices,
    build_ai_assessment_payload,
)
from aws_ai.bedrock_client import BedrockIPv6Client
from network.inventory import load_devices


mcp = MCPServer(
    "IPv6 Readiness Assessment"
)


@mcp.tool()
def list_devices() -> list:
    """
    List all network devices available for IPv6 readiness assessment.
    """

    devices = load_devices()

    return [
        {
            "name": device.name,
            "host": device.host,
            "platform": device.platform,
            "vendor": device.adapter.vendor,
            "role": device.role,
        }
        for device in devices
    ]

@mcp.tool()
def get_device_info(device_name: str) -> str:
    """
    Get basic information about a network device.
    """

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
            f"Device '{device_name}' not found."
        )

    outputs = device.execute_many(device.adapter.get_device_info_commands())
    output = "\n".join(outputs.values())

    return output

@mcp.tool()
def get_ipv6_interfaces(device_name: str) -> str:
    """
    Get IPv6 interface information from a network device.
    """

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
            f"Device '{device_name}' not found."
        )

    outputs = device.execute_many(device.adapter.get_ipv6_interface_commands())
    return "\n".join(outputs.values())

@mcp.tool()
def get_ipv6_routes(device_name: str) -> str:
    """
    Get IPv6 routing table from a network device.
    """

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
            f"Device '{device_name}' not found."
        )

    outputs = device.execute_many(device.adapter.get_ipv6_route_commands())
    return "\n".join(outputs.values())

@mcp.tool()
def get_ipv6_protocols(device_name: str) -> str:
    """
    Get configured IPv6 routing protocols.
    """

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
            f"Device '{device_name}' not found."
        )

    outputs = device.execute_many(device.adapter.get_ipv6_protocol_commands())
    return "\n".join(outputs.values())

@mcp.tool()
def assess_ipv6_device(
    device_name: str
) -> dict:
    """
    Perform a complete IPv6 readiness assessment
    on the specified network device.

    The device is selected from the configured inventory.
    The assessment connects through SSH, collects
    IPv6-related information, parses the device output,
    and executes the deterministic IPv6 assessment engine.
    """

    return assess_device(
        device_name
    )

@mcp.tool()
def assess_all_ipv6_devices() -> str:
    """
    Perform IPv6 readiness assessment on all
    network devices configured in the inventory.

    Returns an overall summary and readiness status
    for each device.
    """

    import json

    result = assess_all_devices()

    return json.dumps(
        result,
        indent=2
    )


@mcp.tool()
def get_ipv6_assessment_payload(
    network_name: str = "IPv6 Readiness Assessment",
) -> dict:
    """Build the complete structured deterministic assessment payload.

    This credential-free payload contains normalized device facts and the
    separate deterministic findings intended for a local AI client.
    """

    return build_ai_assessment_payload(
        assess_all_devices(),
        network_name=network_name,
    )


@mcp.tool()
def run_ipv6_ai_assessment(
    network_name: str = "IPv6 Readiness Assessment",
) -> dict:
    """Run local deterministic assessment then request Bedrock interpretation.

    Collection, parsing, scoring, and MCP execution remain local. AWS is used
    only for the final remote inference request.
    """

    payload = build_ai_assessment_payload(
        assess_all_devices(),
        network_name=network_name,
    )
    return BedrockIPv6Client().assess(payload).to_dict()

if __name__ == "__main__":
    mcp.run()
