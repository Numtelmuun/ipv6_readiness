from network.inventory import load_devices

from parsers.cisco_parser import (
    parse_ipv6_device_data
)


devices = load_devices()


for device in devices:

    print(
        f"\nParsing {device.name}..."
    )

    version = device.execute(
        "show version"
    )

    interfaces = device.execute(
        "show ipv6 interface brief"
    )

    routing = device.execute(
        "show ipv6 route"
    )

    protocols = device.execute(
        "show ipv6 protocols"
    )

    result = parse_ipv6_device_data(
        version_output=version,
        interface_output=interfaces,
        routing_output=routing,
        protocols_output=protocols,
    )

    print("\n===== NORMALIZED RESULT =====")

    print(
        f"Vendor: {result.vendor}"
    )

    print(
        f"Model: {result.model}"
    )

    print(
        f"OS Version: {result.os_version}"
    )

    print(
        f"IPv6 Routing: "
        f"{result.ipv6_routing_enabled}"
    )

    print("\nInterfaces:")

    for interface in result.interfaces:

        print(
            f"  {interface.name}"
        )

        print(
            f"    Operational: "
            f"{interface.operational}"
        )

        print(
            f"    IPv6 enabled: "
            f"{interface.ipv6_enabled}"
        )

        print(
            f"    Link-local: "
            f"{interface.link_local}"
        )

        print(
            f"    Global: "
            f"{interface.global_addresses}"
        )

    print("\nRouting:")

    print(
        f"  Routes: "
        f"{result.routing.route_count}"
    )

    print(
        f"  Connected: "
        f"{result.routing.connected_routes}"
    )

    print(
        f"  Local: "
        f"{result.routing.local_routes}"
    )

    print(
        f"  OSPFv3: "
        f"{result.routing.ospfv3}"
    )

    print(
        f"  RIPng: "
        f"{result.routing.ripng}"
    )

    print(
        f"  EIGRPv6: "
        f"{result.routing.eigrpv6}"
    )

    print(
        f"  BGP IPv6: "
        f"{result.routing.bgp_ipv6}"
    )