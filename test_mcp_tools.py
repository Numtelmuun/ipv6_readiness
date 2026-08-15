import asyncio

from server import mcp


async def main():

    print("=" * 60)
    print("MCP TOOL TEST")
    print("=" * 60)

    # --------------------------------------------------
    # 1. List available tools
    # --------------------------------------------------

    print("\nAvailable MCP tools:")

    tools = await mcp.list_tools()

    for tool in tools:
        print(f"  - {tool.name}")

    # --------------------------------------------------
    # 2. List devices
    # --------------------------------------------------

    print("\n")
    print("=" * 60)
    print("CALL: list_devices")
    print("=" * 60)

    devices = await mcp.call_tool(
        "list_devices",
        {}
    )

    print(devices)

    # --------------------------------------------------
    # 3. Assess R1,R3 devices
    # --------------------------------------------------

    for device_name in ["R1", "R3"]:

        print("\n")
        print("=" * 60)
        print(
            f"CALL: assess_ipv6_device - {device_name}"
        )
        print("=" * 60)

        result = await mcp.call_tool(
            "assess_ipv6_device",
            {
                "device_name": device_name
            }
        )

        print(result)

        print("\n")
        print("=" * 60)
        print("CALL: assess_all_ipv6_devices")
        print("=" * 60)

        result = await mcp.call_tool(
            "assess_all_ipv6_devices",
            {}
        )

        print(result)

if __name__ == "__main__":
    asyncio.run(main())