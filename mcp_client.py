import asyncio
import json

from server import mcp


async def list_tools():
    """List all available MCP tools."""

    tools = await mcp.list_tools()

    print("=" * 60)
    print("AVAILABLE MCP TOOLS")
    print("=" * 60)

    for tool in tools:
        print(f"\nName: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"Input schema: {tool.input_schema}")


async def call_tool(name, arguments):

    result = await mcp.call_tool(
        name,
        arguments
    )

    if result.is_error:
        raise RuntimeError(
            f"MCP tool '{name}' returned an error."
        )

    if not result.content:
        return None

    text = result.content[0].text

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text

async def main():

    await list_tools()

    print("\n")
    print("=" * 60)
    print("CALL: assess_all_ipv6_devices")
    print("=" * 60)

    result = await call_tool(
        "assess_all_ipv6_devices",
        {}
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())