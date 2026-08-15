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