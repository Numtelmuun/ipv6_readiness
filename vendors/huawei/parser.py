"""Fixture-friendly parser for common Huawei VRP IPv6 operational output."""

from __future__ import annotations

import re

from models.device import DeviceInfo, IPv6Interface, IPv6Routing


def parse_version(output: str) -> DeviceInfo:
    device = DeviceInfo(vendor="Huawei", ipv6_supported=None)
    model = re.search(r"^HUAWEI\s+(\S+)\s+uptime", output, re.MULTILINE | re.IGNORECASE)
    if not model:
        model = re.search(r"\((AR\S+)\s+", output, re.IGNORECASE)
    version = re.search(r"Version\s+([\w.()/-]+)", output, re.IGNORECASE)
    device.model = model.group(1) if model else None
    device.os_version = version.group(1) if version else None
    return device


def parse_hostname(output: str) -> str | None:
    match = re.search(r"^sysname\s+(\S+)", output, re.MULTILINE | re.IGNORECASE)
    return match.group(1) if match else None


def parse_interfaces(output: str) -> list[IPv6Interface]:
    interfaces: list[IPv6Interface] = []
    current = None
    for raw_line in output.splitlines():
        line = raw_line.strip()
        header = re.match(r"^(\S+)\s+current state\s*:\s*(UP|DOWN)", line, re.IGNORECASE)
        if header:
            if current:
                interfaces.append(current)
            current = IPv6Interface(
                name=header.group(1),
                operational=header.group(2).upper() == "UP",
                ipv6_enabled=False,
            )
            continue
        if not current:
            continue
        if "IPv6 is enabled" in line:
            current.ipv6_enabled = True
        link_local = re.search(
            r"link-local address is\s+([0-9A-Fa-f:]+)",
            line,
            re.IGNORECASE,
        )
        if link_local:
            current.link_local = link_local.group(1)
            current.ipv6_enabled = True
        address = re.search(r"\b([0-9A-Fa-f:]+::?[0-9A-Fa-f:]*/\d+)\b", line)
        if address:
            value = address.group(1)
            current.ipv6_enabled = True
            if value.lower().startswith("fe80:"):
                current.link_local = value
            else:
                current.global_addresses.append(value)
    if current:
        interfaces.append(current)
    return interfaces


def parse_routing(route_output: str, protocol_output: str = "") -> IPv6Routing:
    routing = IPv6Routing(enabled=None)
    if "Routing Table" in route_output and "Destination/Prefix" in route_output:
        routing.enabled = True
        routes = [
            line for line in route_output.splitlines()
            if re.match(r"^\s*[0-9A-Fa-f].*/\d+", line)
        ]
        routing.route_count = len(routes)
        routing.connected_routes = sum("Direct" in line for line in routes)
        routing.static_routes = sum("Static" in line for line in routes)

    lower = (route_output + "\n" + protocol_output).lower()
    routing.ospfv3 = "ospfv3" in lower
    routing.bgp_ipv6 = "bgp" in lower and "ipv6" in lower
    routing.ripng = "ripng" in lower
    routing.eigrpv6 = "eigrp" in lower
    routing.ipv6_protocols = [
        name
        for name, enabled in (
            ("OSPFv3", routing.ospfv3),
            ("BGP IPv6", routing.bgp_ipv6),
            ("RIPng", routing.ripng),
            ("EIGRPv6", routing.eigrpv6),
        )
        if enabled
    ]
    return routing


def parse_device_data(outputs: dict[str, str]) -> DeviceInfo:
    device = parse_version(outputs.get("display version", ""))
    device.interfaces = parse_interfaces(outputs.get("display ipv6 interface", ""))
    device.routing = parse_routing(
        outputs.get("display ipv6 routing-table", ""),
        outputs.get("display ospfv3 peer", "") + "\n" + outputs.get("display bgp ipv6 routing-table", ""),
    )
    device.hostname = parse_hostname(
        outputs.get("display current-configuration | include sysname", "")
    )
    device.ipv6_routing_enabled = device.routing.enabled
    if any(interface.ipv6_enabled is True for interface in device.interfaces):
        device.ipv6_supported = True
        device.ipv6_addressing_capable = True
        device.ipv6_forwarding_capable = True
        device.ipv6_routing_table_capable = device.routing.enabled
        device.required_ipv6_interfaces = [i.name for i in device.interfaces if i.ipv6_enabled]
    return device
