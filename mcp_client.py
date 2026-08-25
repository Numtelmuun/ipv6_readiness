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


def decode_tool_content(content):
    """Decode every text block returned by an MCP tool.

    MCP represents a list return value as multiple content blocks.  Returning
    only the first block loses data from tools such as ``list_devices``.
    """

    values = []

    for block in content:
        value = getattr(block, "text", None)
        if value is None:
            continue

        try:
            values.append(json.loads(value))
        except json.JSONDecodeError:
            values.append(value)

    if not values:
        return None

    return values[0] if len(values) == 1 else values


async def call_tool(name, arguments):

    result = await mcp.call_tool(
        name,
        arguments
    )

    if result.is_error:
        raise RuntimeError(
            f"MCP tool '{name}' returned an error."
        )

    return decode_tool_content(result.content)

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
