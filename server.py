from mcp.server.mcpserver import MCPServer

from assessment.service import assess_device, assess_all_devices
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

    output = device.execute(
        "show version"
    )

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

    return device.execute(
        "show ipv6 interface brief"
    )

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

    return device.execute(
        "show ipv6 route"
    )

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

    return device.execute(
        "show ipv6 protocols"
    )

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

if __name__ == "__main__":
    mcp.run()