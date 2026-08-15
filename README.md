# IPv6 MCP Assessment

## Project Overview

**Project:** IPv6 Readiness Assessment Automation using Model Context Protocol (MCP)

The project automates the assessment of IPv6 readiness for network devices in a simulated network environment such as **GNS3** or **EVE-NG**.

The system connects to network devices through SSH, collects IPv6-related information, parses the output, evaluates deterministic IPv6 readiness rules, and exposes the assessment functionality through an **MCP server**.

An optional LLM agent can consume the MCP assessment results and generate an AI-assisted IPv6 readiness report.

---

# Architecture

```text
Network Devices
     |
     | SSH / Netmiko
     v
Network Inventory
     |
     v
Collectors
     |
     v
Cisco Parsers
     |
     v
IPv6 Assessment Engine
     |
     +----> Findings
     |
     +----> Score
     |
     +----> Readiness
     |
     +----> Recommendations
     |
     v
Assessment Service
     |
     v
MCP Server
     |
     +----> list_devices
     +----> get_device_info
     +----> get_ipv6_interfaces
     +----> get_ipv6_routes
     +----> get_ipv6_protocols
     +----> assess_ipv6_device
     +----> assess_all_ipv6_devices
     |
     v
LLM Agent
     |
     v
AI IPv6 Readiness Report
```

---

# Project Structure

```text
ipv6-mcp-assessment/
├── assessment/
│   ├── __init__.py
│   ├── engine.py
│   ├── rules.py
│   ├── service.py
│   └── summary.py
│
├── collectors/
│   ├── __init__.py
│   └── ipv6_collector.py
│
├── config/
│   └── devices.yaml
│
├── models/
│   ├── __init__.py
│   ├── assessment.py
│   └── device.py
│
├── network/
│   ├── __init__.py
│   ├── inventory.py
│   └── ssh_client.py
│
├── parsers/
│   ├── __init__.py
│   └── cisco_parser.py
│
├── server.py
├── agent.py
├── llm_agent.py
│
├── test_assessment.py
├── test_inventory.py
├── test_network.py
├── test_normalization.py
├── test_parser.py
├── test_scoring.py
├── test_ssh.py
├── test_unknown.py
└── test_mcp_tools.py
```

---

# Environment

The project uses a Python virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

The project was tested with **Python 3.12**.

The MCP SDK currently installed in the project is:

```text
mcp 2.0.0
```

The OpenAI Python library currently installed is:

```text
openai 3.0.0
```

---

# MCP Server

The project intentionally uses the classic **`MCPServer`** implementation rather than converting the server to `FastMCP`.

The MCP server import works with:

```python
from mcp.server.mcpserver import MCPServer
```

The server object was verified as:

```text
<class 'mcp.server.mcpserver.server.MCPServer'>
```

The available server methods include:

```text
tool
list_tools
call_tool
run
run_stdio_async
run_sse_async
run_streamable_http_async
```

---

# MCP Tools

The project currently exposes the following MCP tools:

```text
list_devices
get_device_info
get_ipv6_interfaces
get_ipv6_routes
get_ipv6_protocols
assess_ipv6_device
assess_all_ipv6_devices
```

---

## `list_devices`

Lists all network devices configured in the inventory.

Example result:

```json
{
  "name": "R1",
  "host": "10.3.132.31",
  "platform": "cisco_ios",
  "role": "edge"
}
```

Another configured device:

```json
{
  "name": "R3",
  "host": "10.3.128.63",
  "platform": "cisco_ios",
  "role": "core"
}
```

---

## `get_device_info`

Retrieves basic information from a network device.

The underlying Cisco command is:

```text
show version
```

---

## `get_ipv6_interfaces`

Retrieves IPv6 interface information.

The Cisco command is:

```text
show ipv6 interface brief
```

---

## `get_ipv6_routes`

Retrieves IPv6 routing information.

The Cisco command is:

```text
show ipv6 route
```

---

## `get_ipv6_protocols`

Retrieves IPv6 routing protocol information.

The Cisco command is:

```text
show ipv6 protocols
```

---

# Device Collection

The collector currently gathers:

```python
def collect_ipv6_data(device):

    return {
        "version": device.execute(
            "show version"
        ),

        "interfaces": device.execute(
            "show ip interface brief"
        ),

        "ipv6_interfaces": device.execute(
            "show ipv6 interface brief"
        ),

        "ipv6_routes": device.execute(
            "show ipv6 route"
        ),
    }
```

The assessment service uses multiple commands:

```python
commands = [
    "show version",
    "show ipv6 interface brief",
    "show ipv6 route",
    "show ipv6 protocols",
    "show running-config | include ^hostname",
]
```

The commands are executed using:

```python
outputs = device.execute_many(commands)
```

This was successfully tested.

Example:

```text
COMMANDS: ['show version', 'show ipv6 interface brief']
VERSION OUTPUT: 1779
INTERFACE OUTPUT: 183
```

---

# Assessment Service

The main assessment function is:

```python
from assessment.service import assess_device
```

Example:

```python
result = assess_device("R1")
print(result)
```

The service:

1. Loads the configured inventory.
2. Finds the requested device.
3. Connects to the device.
4. Collects IPv6-related command output.
5. Parses Cisco output.
6. Normalizes the device data.
7. Applies the IPv6 assessment engine.
8. Generates a finding summary.
9. Returns the final assessment result.

---

# IPv6 Assessment Rules

The assessment currently contains nine IPv6 checks.

```text
IPV6-01  IPv6 interface configuration
IPV6-02  Global IPv6 address
IPV6-03  IPv6 link-local address
IPV6-04  IPv6 routing
IPV6-05  IPv6 dynamic routing
IPV6-06  OSPFv3
IPV6-07  BGP IPv6
IPV6-08  RIPng/EIGRPv6
IPV6-09  Multiple IPv6 interfaces
```

---

# Scoring

The maximum score is based on the applicable checks.

The current scoring weights are:

```text
IPV6-01  20 points
IPV6-02  15 points
IPV6-03  10 points
IPV6-04  20 points
IPV6-05  15 points
IPV6-06   5 points
IPV6-07   5 points
IPV6-08   5 points
IPV6-09   5 points
```

The assessment supports these statuses:

```text
PASS
FAIL
WARNING
UNKNOWN
NOT_APPLICABLE
```

---

# Readiness Levels

The assessment produces a readiness classification such as:

```text
READY
MOSTLY_READY
PARTIALLY_READY
NOT_READY
```

---

# R1 Assessment

R1 is configured as an **edge router**.

The successful assessment result was:

```json
{
  "device": "R1",
  "vendor": "Cisco",
  "model": "1841",
  "os_version": "15.1(4)M9",
  "role": "edge",
  "score": 100.0,
  "readiness": "READY"
}
```

Summary:

```json
{
  "pass": 4,
  "fail": 0,
  "warning": 0,
  "unknown": 0,
  "not_applicable": 5
}
```

The applicable checks all passed:

```text
IPV6-01 PASS
IPV6-02 PASS
IPV6-03 PASS
IPV6-04 PASS
```

The remaining checks were marked **NOT_APPLICABLE** because the device is an edge router and those capabilities are not required by the current assessment logic.

R1 received:

```text
100.0% READY
```

---

# R3 Assessment

R3 is configured as a **core router**.

The successful assessment result was:

```json
{
  "device": "R3",
  "vendor": "Cisco",
  "model": "CISCO1941/K9",
  "os_version": "15.0(1)M4",
  "role": "core",
  "score": 90.0,
  "readiness": "READY"
}
```

Summary:

```json
{
  "pass": 7,
  "fail": 0,
  "warning": 2,
  "unknown": 0,
  "not_applicable": 0
}
```

R3 has:

```text
2 IPv6-enabled interfaces
2 global IPv6 addresses
2 link-local addresses
IPv6 routing enabled
OSPFv3 detected
```

Warnings:

```text
IPV6-07 WARNING
IPv6 BGP not detected.

IPV6-08 WARNING
Neither RIPng nor EIGRPv6 detected.
```

The resulting score is:

```text
90.0% READY
```

---

# Recommendations

The assessment engine can generate recommendations from warnings.

For R3, the current recommendations are:

```json
[
  {
    "id": "IPV6-07",
    "severity": "LOW",
    "recommendation": "Configure IPv6 BGP only if this device requires external IPv6 routing."
  },
  {
    "id": "IPV6-08",
    "severity": "LOW",
    "recommendation": "Configure RIPng or EIGRPv6 only if required by the network routing design."
  }
]
```

These recommendations are conditional and do not mean that BGP, RIPng, or EIGRPv6 must automatically be configured.

---

# Assess All Devices

The MCP tool:

```text
assess_all_ipv6_devices
```

runs the assessment across the configured inventory.

Current inventory:

```text
R1
R3
```

Successful aggregate result:

```json
{
  "summary": {
    "total_devices": 2,
    "ready": 2,
    "mostly_ready": 0,
    "partially_ready": 0,
    "not_ready": 0
  },
  "average_score": 95.0,
  "recommendation_count": 2
}
```

Device results:

```text
R1    edge    100.0% READY
R3    core     90.0% READY
```

Overall:

```text
Average score: 95.0%
READY: 2
```

---

# Testing MCP Tools

The MCP tools can be tested directly without starting an external MCP client.

The test script uses asynchronous MCP methods.

Example:

```python
import asyncio

from server import mcp


async def main():

    tools = await mcp.list_tools()

    for tool in tools:
        print(tool.name)

    result = await mcp.call_tool(
        "list_devices",
        {}
    )

    print(result)


if __name__ == "__main__":
    asyncio.run(main())
```

Run:

```bash
python test_mcp_tools.py
```

The available tools were successfully verified:

```text
Available MCP tools:
  - list_devices
  - get_device_info
  - get_ipv6_interfaces
  - get_ipv6_routes
  - get_ipv6_protocols
  - assess_ipv6_device
  - assess_all_ipv6_devices
```

---

# Important MCP SDK Detail

With the installed **MCP 2.0.0** SDK:

```python
mcp.list_tools()
```

returns a coroutine.

Therefore, this:

```python
print(mcp.list_tools())
```

does not directly return the tool list.

Instead use:

```python
import asyncio

print(asyncio.run(mcp.list_tools()))
```

The returned value is a list of `Tool` objects.

Therefore, this is incorrect:

```python
result = await mcp.list_tools()

for tool in result.tools:
    ...
```

The correct approach is:

```python
result = await mcp.list_tools()

for tool in result:
    print(tool.name)
```

---

# MCP Server Verification

The MCP server can be imported with:

```bash
python -c "from server import mcp; print('MCP SERVER IMPORT OK')"
```

Expected:

```text
MCP SERVER IMPORT OK
```

The MCP object type is:

```text
<class 'mcp.server.mcpserver.server.MCPServer'>
```

---

# Network Connectivity

The project successfully connects to the Cisco devices through SSH.

Example connection output:

```text
INFO Connected (version 2.0, client Cisco-1.25)
INFO Authentication (password) successful!
```

The assessment therefore currently has an end-to-end flow:

```text
MCP Tool
   |
   v
Assessment Service
   |
   v
Inventory
   |
   v
SSH / Netmiko
   |
   v
Cisco Router
   |
   v
Command Output
   |
   v
Parser
   |
   v
Assessment Engine
   |
   v
Score + Findings + Recommendations
```

---

# AI Agent

An additional AI agent was developed to consume the assessment results and produce an AI-oriented IPv6 readiness report.

The project contains:

```text
agent.py
llm_agent.py
```

The non-LLM report successfully produced:

```text
============================================================
AI IPv6 READINESS REPORT
============================================================

Total devices: 2
Average score: 95.0%

Readiness:
  READY:           2
  MOSTLY_READY:    0
  PARTIALLY_READY: 0
  NOT_READY:       0

Devices:
  R1    edge  100.0% READY
  R3    core   90.0% READY

Recommendations:
  [LOW] R3 - IPV6-07
      Configure IPv6 BGP only if this device requires external IPv6 routing.

  [LOW] R3 - IPV6-08
      Configure RIPng or EIGRPv6 only if required by the network routing design.
```

---

# OpenAI API Integration

The project uses the official OpenAI Python package.

Installed version:

```text
openai 3.0.0
```

The project uses the OpenAI Responses API.

The API call was observed as:

```text
POST https://api.openai.com/v1/responses
```

The LLM agent therefore requires a valid OpenAI API key and an account/project with available API quota.

---

# API Key

An OpenAI API key is different from a normal ChatGPT subscription login.

The key should be created from the OpenAI API platform and supplied to the application through an environment variable.

Example:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

Then verify that the environment variable exists:

```bash
echo $OPENAI_API_KEY
```

Do **not** commit the API key into Git.

A `.env` file should also be excluded from source control if it is used.

Example `.gitignore` entry:

```gitignore
.env
.venv/
__pycache__/
*.pyc
```

---

# OpenAI API Quota Issue

During testing, the LLM agent returned:

```text
HTTP/1.1 429 Too Many Requests
```

The important error was:

```text
Error code: 429

{
  "error": {
    "message": "You exceeded your current quota, please check your plan and billing details.",
    "type": "insufficient_quota",
    "param": null,
    "code": "insufficient_quota"
  }
}
```

This is specifically an **`insufficient_quota`** error.

It is not necessarily caused by sending requests too quickly.

The API account/project needs available API quota or billing capacity.

The MCP and IPv6 assessment portions of the project were working independently of this OpenAI API quota issue.

---

# Current End-to-End Status

The following components have been successfully tested:

```text
[OK] Python virtual environment
[OK] Network inventory
[OK] Cisco SSH connection
[OK] Netmiko command execution
[OK] Cisco IPv6 data collection
[OK] Cisco output parsing
[OK] IPv6 assessment engine
[OK] Deterministic scoring
[OK] Finding summaries
[OK] Recommendations
[OK] MCPServer
[OK] MCP tool registration
[OK] MCP list_devices
[OK] MCP device assessment
[OK] MCP assessment of all devices
[OK] AI-style aggregate readiness report
```

The remaining issue encountered during LLM testing was:

```text
[BLOCKED] OpenAI API quota / billing
```

---

# Example Complete Workflow

Start the project environment:

```bash
cd ipv6-mcp-assessment

source .venv/bin/activate
```

Verify MCP:

```bash
python -c "from server import mcp; print('MCP SERVER IMPORT OK')"
```

Run MCP tests:

```bash
python test_mcp_tools.py
```

Run the assessment agent:

```bash
python agent.py
```

For LLM-based functionality, configure:

```bash
export OPENAI_API_KEY="your_api_key_here"
```

Then run:

```bash
python llm_agent.py
```

---

# Example Expected Final Report

```text
============================================================
AI IPv6 READINESS REPORT
============================================================

Total devices: 2
Average score: 95.0%

Readiness:
  READY:           2
  MOSTLY_READY:    0
  PARTIALLY_READY: 0
  NOT_READY:       0

Devices:
  R1    edge  100.0% READY
  R3    core   90.0% READY

Recommendations:
  [LOW] R3 - IPV6-07
      Configure IPv6 BGP only if this device requires external IPv6 routing.

  [LOW] R3 - IPV6-08
      Configure RIPng or EIGRPv6 only if required by the network routing design.
```

---

# Project Goal

The final objective of the project is to demonstrate how **Model Context Protocol (MCP)** can be used to provide an AI agent with structured tools for network-device assessment.

The intended architecture separates responsibilities:

```text
Network Access
      |
      v
Data Collection
      |
      v
Data Parsing
      |
      v
Deterministic Assessment
      |
      v
MCP Tools
      |
      v
AI Agent
      |
      v
Human-readable IPv6 Readiness Report
```

This separation allows the network assessment logic to remain **deterministic and reproducible**, while the AI layer can focus on interpreting the assessment results and communicating recommendations.

---

# Current Test Topology

```text
                 IPv6 Network
                     |
          +----------+----------+
          |                     |
         R1                    R3
       Edge                  Core
      Cisco 1841          Cisco 1941/K9
          |                     |
      100% READY             90% READY
          |                     |
          +----------+----------+
                     |
                 MCP Server
                     |
                 AI Agent
```

---

# Summary

The project has progressed from a basic MCP server to a working **end-to-end IPv6 readiness assessment system**.

The current implementation successfully:

- Connects to Cisco devices.
- Collects IPv6 information.
- Parses device information.
- Evaluates IPv6 readiness.
- Calculates readiness scores.
- Generates findings.
- Generates recommendations.
- Exposes assessment functionality through MCP.
- Assesses multiple devices.
- Produces an aggregate network readiness report.
- Provides a foundation for LLM-based interpretation.

Current test results:

```text
R1: 100% READY
R3:  90% READY

Network average: 95%

Total devices: 2
Ready devices: 2
Recommendations: 2
```

The next major integration point is the **LLM agent**, which requires an OpenAI API project with available API quota.
