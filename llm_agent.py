import asyncio
import json
import os

from openai import OpenAI

from mcp_client import call_tool


client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)


MODEL = "gpt-5.6"


TOOLS = [
    {
        "type": "function",
        "name": "list_devices",
        "description": (
            "List all network devices available for "
            "IPv6 readiness assessment."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_device_info",
        "description": (
            "Get basic information about a network device."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "device_name": {
                    "type": "string",
                    "description": "Network device name, for example R1 or R3.",
                }
            },
            "required": ["device_name"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_ipv6_interfaces",
        "description": (
            "Get IPv6 interface information from a network device."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "device_name": {
                    "type": "string",
                    "description": "Network device name.",
                }
            },
            "required": ["device_name"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_ipv6_routes",
        "description": (
            "Get IPv6 routing information from a network device."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "device_name": {
                    "type": "string",
                    "description": "Network device name.",
                }
            },
            "required": ["device_name"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "get_ipv6_protocols",
        "description": (
            "Get IPv6 routing protocol information from a network device."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "device_name": {
                    "type": "string",
                    "description": "Network device name.",
                }
            },
            "required": ["device_name"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "assess_ipv6_device",
        "description": (
            "Perform a complete IPv6 readiness assessment "
            "for a specific network device."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "device_name": {
                    "type": "string",
                    "description": "Network device name.",
                }
            },
            "required": ["device_name"],
            "additionalProperties": False,
        },
    },
    {
        "type": "function",
        "name": "assess_all_ipv6_devices",
        "description": (
            "Perform IPv6 readiness assessment on all "
            "devices in the configured inventory."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "additionalProperties": False,
        },
    },
]


async def execute_tool(name, arguments):

    return await call_tool(
        name,
        arguments
    )


async def ask_agent(question):

    response = client.responses.create(
        model=MODEL,
        instructions=(
            "You are an IPv6 network assessment assistant. "
            "Use the available tools to inspect network devices "
            "and perform IPv6 readiness assessments. "
            "Do not invent network information. "
            "Base technical conclusions on tool results. "
            "Answer the user in Mongolian."
        ),
        input=question,
        tools=TOOLS,
    )

    while True:

        tool_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not tool_calls:
            return response.output_text

        tool_outputs = []

        for tool_call in tool_calls:

            name = tool_call.name

            arguments = json.loads(
                tool_call.arguments
            )

            print(
                f"\n[AI TOOL CALL] "
                f"{name}({arguments})"
            )

            result = await execute_tool(
                name,
                arguments
            )

            tool_outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": json.dumps(
                        result,
                        ensure_ascii=False
                    ),
                }
            )

        response = client.responses.create(
            model=MODEL,
            instructions=(
                "You are an IPv6 network assessment assistant. "
                "Use the available tools to inspect network devices "
                "and perform IPv6 readiness assessments. "
                "Do not invent network information. "
                "Base technical conclusions on tool results. "
                "Answer the user in Mongolian."
            ),
            previous_response_id=response.id,
            input=tool_outputs,
            tools=TOOLS,
        )


async def main():

    print("=" * 60)
    print("IPv6 AI AGENT")
    print("=" * 60)

    question = input(
        "\nАсуултаа оруулна уу: "
    )

    answer = await ask_agent(
        question
    )

    print("\n")
    print("=" * 60)
    print("AI RESPONSE")
    print("=" * 60)
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())