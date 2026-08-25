import re

from models.device import (
    DeviceInfo,
    IPv6Interface,
    IPv6Routing,
)


def parse_show_version(output: str) -> DeviceInfo:

    device = DeviceInfo(
        vendor="Cisco"
    )

    # IOS version
    version_match = re.search(
        r"Version\s+([\w().-]+)",
        output
    )

    if version_match:
        device.os_version = (
            version_match.group(1)
        )   

    # Cisco model
    model_match = re.search(
        r"Cisco\s+(\S+)\s+\(revision",
        output
    )

    if model_match:
        device.model = (
            model_match.group(1)
        )

    # IPv6 capability will be determined
    # from feature/configuration checks later.
    device.ipv6_supported = None

    return device

def parse_ipv6_interface_brief(
    output: str
) -> list[IPv6Interface]:

    interfaces = []

    current = None

    for line in output.splitlines():

        line = line.strip()

        if not line:
            continue

        # Interface line
        match = re.match(
            r"^(\S+)\s+\[(up|down)/(up|down)\]$",
            line
        )

        if match:

            if current:
                interfaces.append(current)

            name = match.group(1)

            status = match.group(2)
            protocol = match.group(3)

            current = IPv6Interface(
                name=name,
                operational=(
                    status == "up"
                    and protocol == "up"
                )
            )

            continue

        if current:

            if line.lower() == "unassigned":
                continue

            # Link-local
            if line.upper().startswith("FE80:"):
                current.link_local = line
                current.ipv6_enabled = True
                continue

            # Global IPv6 address
            if ":" in line:
                current.global_addresses.append(
                    line
                )

                current.ipv6_enabled = True

    if current:
        interfaces.append(current)

    return interfaces
def parse_ipv6_routing(
    output: str
) -> IPv6Routing:

    # No routing-table header means collection could not establish the state;
    # preserve that distinction instead of treating it as disabled.
    routing = IPv6Routing(enabled=None)

    if "IPv6 Routing Table" not in output:
        return routing

    routing.enabled = True

    # Number of routes
    count_match = re.search(
        r"IPv6 Routing Table.*?(\d+)\s+entries",
        output
    )

    if count_match:
        routing.route_count = int(
            count_match.group(1)
        )

    for line in output.splitlines():

        line = line.strip()

        if line.startswith("C "):
            routing.connected_routes += 1

        elif line.startswith("L "):
            routing.local_routes += 1

        elif line.startswith("S "):
            routing.static_routes += 1

        elif line.startswith("O "):
            routing.ospfv3 = True

        elif line.startswith("D "):
            routing.eigrpv6 = True

        elif line.startswith("R "):
            routing.ripng = True

        elif line.startswith("B "):
            routing.bgp_ipv6 = True

    return routing

def parse_ipv6_protocols(
    output: str,
    routing: IPv6Routing
) -> IPv6Routing:

    text = output.lower()

    routing.ospfv3 = (
        "ospf" in text
    )

    routing.ripng = (
        "rip" in text
    )

    routing.eigrpv6 = (
        "eigrp" in text
    )

    routing.bgp_ipv6 = (
        "bgp" in text
    )

    return routing
def parse_ipv6_device_data(
    version_output: str,
    interface_output: str,
    routing_output: str,
    protocols_output: str,
) -> DeviceInfo:

    device = parse_show_version(
        version_output
    )

    device.interfaces = (
        parse_ipv6_interface_brief(
            interface_output
        )
    )

    device.routing = (
        parse_ipv6_routing(
            routing_output
        )
    )

    device.routing = (
        parse_ipv6_protocols(
            protocols_output,
            device.routing
        )
    )

    device.ipv6_routing_enabled = (
        device.routing.enabled
    )

    return device

def parse_hostname(output: str) -> str | None:

    import re

    match = re.search(
        r"^hostname\s+(\S+)",
        output,
        re.MULTILINE
    )

    if match:
        return match.group(1)

    return None
