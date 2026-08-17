from dataclasses import dataclass, field


@dataclass
class NormalizedInterface:
    name: str

    ipv6_enabled: bool = False

    global_addresses: list[str] = field(
        default_factory=list
    )

    link_local_addresses: list[str] = field(
        default_factory=list
    )


@dataclass
class NormalizedRoutingProtocols:
    ospfv3: bool = False

    bgp_ipv6: bool = False

    ripng: bool = False

    eigrpv6: bool = False


@dataclass
class NormalizedDevice:
    hostname: str

    vendor: str

    model: str

    os_version: str

    role: str | None = None

    interfaces: list[NormalizedInterface] = field(
        default_factory=list
    )

    ipv6_routing_enabled: bool = False

    routing_protocols: NormalizedRoutingProtocols = field(
        default_factory=NormalizedRoutingProtocols
    )