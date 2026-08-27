from models.device import DeviceInfo


PROTOCOL_ALIASES = {
    "ospf": "ospfv3",
    "ospfv3": "ospfv3",
    "bgp": "bgp_ipv6",
    "bgp ipv6": "bgp_ipv6",
    "ipv6 bgp": "bgp_ipv6",
    "bgp_ipv6": "bgp_ipv6",
    "ripng": "ripng",
    "eigrpv6": "eigrpv6",
}


def required_protocols(device: DeviceInfo) -> set[str]:
    return {
        PROTOCOL_ALIASES.get(str(protocol).strip().lower(), str(protocol).strip().lower())
        for protocol in device.required_routing_protocols
    }


def detected_protocols(device: DeviceInfo) -> set[str]:
    return {
        name
        for name in ("ospfv3", "ripng", "eigrpv6", "bgp_ipv6")
        if getattr(device.routing, name)
    }


def check_ipv6_interfaces(device: DeviceInfo):

    if not device.interfaces:

        return {
            "id": "IPV6-01",
            "name": "IPv6 interface configuration",
            "status": "UNKNOWN",
            "score": 0,
            "max_score": 20,
            "message": (
                "Interface information could not "
                "be determined."
            ),
        }

    unknown_interfaces = [
        interface
        for interface in device.interfaces
        if interface.ipv6_enabled is None
    ]

    if unknown_interfaces:

        return {
            "id": "IPV6-01",
            "name": "IPv6 interface configuration",
            "status": "UNKNOWN",
            "score": 0,
            "max_score": 20,
            "message": (
                f"{len(unknown_interfaces)} interface(s) "
                "have unknown IPv6 configuration state."
            ),
        }

    enabled_interfaces = [
        interface
        for interface in device.interfaces
        if interface.ipv6_enabled
    ]

    if len(enabled_interfaces) == 0:

        return {
            "id": "IPV6-01",
            "name": "IPv6 interface configuration",
            "status": "FAIL",
            "score": 0,
            "max_score": 20,
            "message": (
                "No interface has IPv6 enabled."
            ),
        }

    return {
        "id": "IPV6-01",
        "name": "IPv6 interface configuration",
        "status": "PASS",
        "score": 20,
        "max_score": 20,
        "message": (
            f"{len(enabled_interfaces)} interface(s) "
            "have IPv6 enabled."
        ),
    }

def check_global_ipv6_address(device: DeviceInfo):

    if not device.interfaces:
        return {
            "id": "IPV6-02",
            "name": "Global IPv6 address",
            "status": "UNKNOWN",
            "score": 0,
            "max_score": 15,
            "message": (
                "Interface information could not "
                "be determined."
            ),
        }

    addresses = []

    for interface in device.interfaces:
        addresses.extend(
            interface.global_addresses
        )

    if not addresses:
        return {
            "id": "IPV6-02",
            "name": "Global IPv6 address",
            "status": "FAIL",
            "score": 0,
            "max_score": 15,
            "message": (
                "No global IPv6 address "
                "was detected."
            ),
        }

    return {
        "id": "IPV6-02",
        "name": "Global IPv6 address",
        "status": "PASS",
        "score": 15,
        "max_score": 15,
        "message": (
            f"{len(addresses)} global IPv6 "
            "address(es) detected."
        ),
    }


def check_link_local(device: DeviceInfo):

    if not device.interfaces:
        return {
            "id": "IPV6-03",
            "name": "IPv6 link-local address",
            "status": "UNKNOWN",
            "score": 0,
            "max_score": 10,
            "message": (
                "Interface information could not "
                "be determined."
            ),
        }

    interfaces_with_link_local = [
        interface
        for interface in device.interfaces
        if interface.link_local
    ]

    if not interfaces_with_link_local:
        return {
            "id": "IPV6-03",
            "name": "IPv6 link-local address",
            "status": "FAIL",
            "score": 0,
            "max_score": 10,
            "message": (
                "No IPv6 link-local address detected."
            ),
        }

    return {
        "id": "IPV6-03",
        "name": "IPv6 link-local address",
        "status": "PASS",
        "score": 10,
        "max_score": 10,
        "message": (
            f"{len(interfaces_with_link_local)} "
            "interface(s) have link-local addresses."
        ),
    }


def check_ipv6_routing(device: DeviceInfo):

    if device.ipv6_routing_enabled is None:
        return {
            "id": "IPV6-04",
            "name": "IPv6 routing",
            "status": "UNKNOWN",
            "score": 0,
            "max_score": 20,
            "message": (
                "IPv6 routing state could not "
                "be determined."
            ),
        }

    if not device.ipv6_routing_enabled:
        return {
            "id": "IPV6-04",
            "name": "IPv6 routing",
            "status": "FAIL",
            "score": 0,
            "max_score": 20,
            "message": (
                "IPv6 routing is not enabled."
            ),
        }

    return {
        "id": "IPV6-04",
        "name": "IPv6 routing",
        "status": "PASS",
        "score": 20,
        "max_score": 20,
        "message": (
            "IPv6 routing is enabled."
        ),
    }


def check_dynamic_routing(device):

    dynamic_protocols = []

    if device.routing.ospfv3:
        dynamic_protocols.append("OSPFv3")

    if device.routing.ripng:
        dynamic_protocols.append("RIPng")

    if device.routing.eigrpv6:
        dynamic_protocols.append("EIGRPv6")

    if device.routing.bgp_ipv6:
        dynamic_protocols.append("BGP IPv6")

    required = required_protocols(device)
    missing_required = required - detected_protocols(device)

    if not required and not dynamic_protocols:

        return {
            "id": "IPV6-05",
            "name": "IPv6 dynamic routing",
            "status": "NOT_APPLICABLE",
            "score": 0,
            "max_score": 15,
            "message": (
                "No dynamic IPv6 routing protocol is explicitly required "
                "for this device."
            ),
        }

    if dynamic_protocols and not missing_required:

        return {
            "id": "IPV6-05",
            "name": "IPv6 dynamic routing",
            "status": "PASS",
            "score": 15,
            "max_score": 15,
            "message": (
                "Detected: "
                + ", ".join(dynamic_protocols)
            ),
        }

    return {
        "id": "IPV6-05",
        "name": "IPv6 dynamic routing",
        "status": "WARNING",
        "score": 0,
        "max_score": 15,
        "message": (
            "Required IPv6 routing protocol(s) not detected: "
            + ", ".join(sorted(missing_required))
        ),
    }
def check_ospfv3(device):

    if "ospfv3" not in required_protocols(device) and not device.routing.ospfv3:

        return {
            "id": "IPV6-06",
            "name": "OSPFv3",
            "status": "NOT_APPLICABLE",
            "score": 0,
            "max_score": 5,
            "message": (
                "OSPFv3 is not explicitly required for this device."
            ),
        }

    if device.routing.ospfv3:

        return {
            "id": "IPV6-06",
            "name": "OSPFv3",
            "status": "PASS",
            "score": 5,
            "max_score": 5,
            "message": "OSPFv3 detected.",
        }

    return {
        "id": "IPV6-06",
        "name": "OSPFv3",
        "status": "WARNING",
        "score": 0,
        "max_score": 5,
        "message": "OSPFv3 not detected.",
    }
def check_bgp_ipv6(device):

    if "bgp_ipv6" not in required_protocols(device) and not device.routing.bgp_ipv6:

        return {
            "id": "IPV6-07",
            "name": "BGP IPv6",
            "status": "NOT_APPLICABLE",
            "score": 0,
            "max_score": 5,
            "message": (
                "IPv6 BGP is not explicitly required for this device."
            ),
        }

    if device.routing.bgp_ipv6:

        return {
            "id": "IPV6-07",
            "name": "BGP IPv6",
            "status": "PASS",
            "score": 5,
            "max_score": 5,
            "message": "IPv6 BGP detected.",
        }

    return {
        "id": "IPV6-07",
        "name": "BGP IPv6",
        "status": "WARNING",
        "score": 0,
        "max_score": 5,
        "message": "IPv6 BGP not detected.",
    }
def check_other_dynamic_routing(device):

    required = required_protocols(device) & {"ripng", "eigrpv6"}
    detected = detected_protocols(device) & {"ripng", "eigrpv6"}

    if required - detected:

        return {
            "id": "IPV6-08",
            "name": "RIPng/EIGRPv6",
            "status": "WARNING",
            "score": 0,
            "max_score": 5,
            "message": (
                "Required routing protocol(s) not detected: "
                + ", ".join(sorted(required - detected))
            ),
        }

    if device.routing.ripng:

        return {
            "id": "IPV6-08",
            "name": "RIPng/EIGRPv6",
            "status": "PASS",
            "score": 5,
            "max_score": 5,
            "message": "RIPng detected.",
        }

    if device.routing.eigrpv6:

        return {
            "id": "IPV6-08",
            "name": "RIPng/EIGRPv6",
            "status": "PASS",
            "score": 5,
            "max_score": 5,
            "message": "EIGRPv6 detected.",
        }

    if not required:

        return {
            "id": "IPV6-08",
            "name": "RIPng/EIGRPv6",
            "status": "NOT_APPLICABLE",
            "score": 0,
            "max_score": 5,
            "message": (
                "RIPng/EIGRPv6 is not explicitly required for this device."
            ),
        }

    raise AssertionError("required RIPng/EIGRPv6 state was not resolved")
def check_multiple_ipv6_interfaces(device: DeviceInfo):

    if not device.interfaces:
        return {
            "id": "IPV6-09",
            "name": "Multiple IPv6 interfaces",
            "status": "UNKNOWN",
            "score": 0,
            "max_score": 5,
            "message": (
                "Interface information could not "
                "be determined."
            ),
        }

    count = sum(
        1
        for interface in device.interfaces
        if interface.ipv6_enabled
    )

    if device.role == "edge" and count >= 1:

        return {
            "id": "IPV6-09",
            "name": "Multiple IPv6 interfaces",
            "status": "NOT_APPLICABLE",
            "score": 0,
            "max_score": 5,
            "message": (
                "Multiple IPv6 interfaces are not "
                "required for this edge router."
            ),
        }

    if count >= 2:

        return {
            "id": "IPV6-09",
            "name": "Multiple IPv6 interfaces",
            "status": "PASS",
            "score": 5,
            "max_score": 5,
            "message": (
                f"{count} IPv6-enabled interfaces detected."
            ),
        }

    return {
        "id": "IPV6-09",
        "name": "Multiple IPv6 interfaces",
        "status": "WARNING",
        "score": 0,
        "max_score": 5,
        "message": (
            f"Only {count} IPv6-enabled "
            "interface detected."
        ),
    }
