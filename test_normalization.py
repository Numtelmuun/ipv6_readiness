from network.inventory import load_devices

from parsers.cisco_parser import (
    parse_ipv6_device_data,
)


devices = load_devices()


for device in devices:

    print("\n" + "=" * 60)
    print(f"DEVICE: {device.name}")
    print(f"ROLE: {device.role}")
    print("=" * 60)

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

    normalized = parse_ipv6_device_data(
        version_output=version,
        interface_output=interfaces,
        routing_output=routing,
        protocols_output=protocols,
    )

    normalized.hostname = device.name
    normalized.role = device.role

    print(f"Vendor: {normalized.vendor}")
    print(f"Model: {normalized.model}")
    print(f"OS: {normalized.os_version}")

    print(
        f"IPv6 supported: "
        f"{normalized.ipv6_supported}"
    )

    print(
        f"IPv6 routing enabled: "
        f"{normalized.ipv6_routing_enabled}"
    )

    print("\nInterfaces:")

    for interface in normalized.interfaces:

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
        f"  Route count: "
        f"{normalized.routing.route_count}"
    )

    print(
        f"  Connected routes: "
        f"{normalized.routing.connected_routes}"
    )

    print(
        f"  Local routes: "
        f"{normalized.routing.local_routes}"
    )

    print(
        f"  Static routes: "
        f"{normalized.routing.static_routes}"
    )

    print(
        f"  OSPFv3: "
        f"{normalized.routing.ospfv3}"
    )

    print(
        f"  RIPng: "
        f"{normalized.routing.ripng}"
    )

    print(
        f"  EIGRPv6: "
        f"{normalized.routing.eigrpv6}"
    )

    print(
        f"  BGP IPv6: "
        f"{normalized.routing.bgp_ipv6}"
    )