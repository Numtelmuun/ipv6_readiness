"""Fixture-friendly parser for common Junos IPv6 operational output."""

from __future__ import annotations

import re

from models.device import DeviceInfo, IPv6Interface, IPv6Routing


def parse_version(output: str) -> DeviceInfo:
    device = DeviceInfo(vendor="Juniper", ipv6_supported=None)
    hostname = re.search(r"^Hostname:\s*(\S+)", output, re.MULTILINE)
    model = re.search(r"^Model:\s*(\S+)", output, re.MULTILINE)
    version = re.search(r"^Junos:\s*(\S+)", output, re.MULTILINE)
    device.hostname = hostname.group(1) if hostname else None
    device.model = model.group(1) if model else None
    device.os_version = version.group(1) if version else None
    return device


def parse_interfaces(terse_output: str, detail_output: str = "") -> list[IPv6Interface]:
    interfaces: dict[str, IPv6Interface] = {}

    for raw_line in terse_output.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("Interface"):
            continue
        fields = line.split()
        if len(fields) < 3 or fields[0].startswith("{"):
            continue

        name, admin_state, link_state = fields[:3]
        interface = interfaces.setdefault(
            name,
            IPv6Interface(
                name=name,
                operational=admin_state.lower() == "up" and link_state.lower() == "up",
                ipv6_enabled=False,
            ),
        )
        family = fields[3].lower() if len(fields) > 3 else ""
        address = fields[4] if len(fields) > 4 else ""
        if family != "inet6":
            continue

        interface.ipv6_enabled = True
        if address.lower().startswith("fe80:"):
            interface.link_local = address
        elif ":" in address:
            interface.global_addresses.append(address)

    # Detail output can identify an enabled inet6 family even when terse output
    # omits an address (for example, before address assignment completes).
    current = None
    for raw_line in detail_output.splitlines():
        match = re.search(r"Physical interface:\s*(\S+),.*Physical link is (Up|Down)", raw_line)
        if match:
            current = match.group(1)
            continue
        logical = re.search(r"Logical interface\s+(\S+)", raw_line)
        if logical:
            current = logical.group(1)
            continue
        if current and "inet6" in raw_line.lower():
            interface = interfaces.get(current)
            if interface:
                interface.ipv6_enabled = True

    return list(interfaces.values())


def parse_routing(route_output: str, protocol_output: str = "") -> IPv6Routing:
    routing = IPv6Routing(enabled=None)
    text = route_output + "\n" + protocol_output
    if "inet6.0:" in route_output:
        routing.enabled = True
        count = re.search(r"inet6\.0:\s*(\d+) destinations,\s*(\d+) routes", route_output)
        if count:
            routing.route_count = int(count.group(2))
        routing.connected_routes = len(re.findall(r"\bDirect\b", route_output))
        routing.static_routes = len(re.findall(r"\bStatic\b", route_output))

    lower = text.lower()
    routing.ospfv3 = "ospf3" in lower
    routing.bgp_ipv6 = "bgp" in lower and ("inet6" in lower or "inet6.0" in lower)
    routing.ripng = "ripng" in lower
    routing.eigrpv6 = False
    routing.ipv6_protocols = [
        name
        for name, enabled in (
            ("OSPFv3", routing.ospfv3),
            ("BGP IPv6", routing.bgp_ipv6),
            ("RIPng", routing.ripng),
        )
        if enabled
    ]
    return routing


def parse_device_data(outputs: dict[str, str]) -> DeviceInfo:
    device = parse_version(outputs.get("show version", ""))
    device.interfaces = parse_interfaces(
        outputs.get("show interfaces terse", ""),
        outputs.get("show interfaces detail", ""),
    )
    device.routing = parse_routing(
        outputs.get("show route table inet6.0", ""),
        outputs.get("show ospf3 overview", "") + "\n" + outputs.get("show bgp summary", ""),
    )
    device.ipv6_routing_enabled = device.routing.enabled
    if any(interface.ipv6_enabled is True for interface in device.interfaces):
        device.ipv6_supported = True
    return device
