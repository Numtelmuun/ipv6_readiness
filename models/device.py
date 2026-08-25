from dataclasses import dataclass, field
from typing import Optional


@dataclass
class IPv6Interface:
    name: str
    operational: bool = False
    ipv6_enabled: Optional[bool] = False
    link_local: Optional[str] = None
    global_addresses: list[str] = field(
        default_factory=list
    )
    prefix_lengths: list[int] = field(
        default_factory=list
    )
    router_advertisements: bool = False
    dad_enabled: bool = False


@dataclass
class IPv6Routing:
    enabled: Optional[bool] = False
    route_count: int = 0
    connected_routes: int = 0
    local_routes: int = 0
    static_routes: int = 0
    ospfv3: bool = False
    ripng: bool = False
    eigrpv6: bool = False
    bgp_ipv6: bool = False
    # Protocol names retain vendor-neutral context for reporting/AI while the
    # boolean fields above keep the existing deterministic rules unchanged.
    ipv4_protocols: list[str] = field(
        default_factory=list
    )
    ipv6_protocols: list[str] = field(
        default_factory=list
    )

@dataclass
class DeviceInfo:

    hostname: Optional[str] = None
    vendor: Optional[str] = None
    model: Optional[str] = None
    os_version: Optional[str] = None

    role: Optional[str] = None

    ipv6_supported: Optional[bool] = None
    ipv6_routing_enabled: Optional[bool] = None

    interfaces: list[IPv6Interface] = field(
        default_factory=list
    )

    routing: IPv6Routing = field(
        default_factory=IPv6Routing
    )
