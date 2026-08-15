from network.inventory import load_devices

from parsers.cisco_parser import (
    parse_ipv6_device_data,
    parse_hostname,
)

from assessment.engine import assess_ipv6


devices = load_devices()


for device in devices:

    print(
        f"\nCollecting data from {device.name}..."
    )

    # Collect raw data
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

    hostname_output = device.execute(
        "show running-config | include ^hostname"
    )

    # Parse raw data
    normalized = parse_ipv6_device_data(
        version_output=version,
        interface_output=interfaces,
        routing_output=routing,
        protocols_output=protocols,
    )

    # Add inventory/context information
    normalized.hostname = (
        parse_hostname(hostname_output)
        or device.name
    )

    normalized.role = device.role

    # Run assessment
    result = assess_ipv6(
        normalized
    )

    # Display result
    print("\n")
    print("=" * 60)
    print("IPv6 READINESS ASSESSMENT")
    print("=" * 60)

    print(
        f"Device: {result['device']}"
    )

    print(
        f"Role: {normalized.role}"
    )

    print(
        f"Vendor: {result['vendor']}"
    )

    print(
        f"Model: {result['model']}"
    )

    print(
        f"OS: {result['os_version']}"
    )

    print(
        f"\nScore: {result['score']}%"
    )

    print(
        f"Readiness: {result['readiness']}"
    )

    print("\nFindings:")

    for finding in result["findings"]:

        print(
            f"[{finding['status']}] "
            f"{finding['id']} - "
            f"{finding['name']}"
        )

        print(
            f"    {finding['message']}"
        )