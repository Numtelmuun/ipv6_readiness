from models.device import DeviceInfo, IPv6Interface, IPv6Routing
from assessment.engine import assess_ipv6


def create_unknown_device():

    return DeviceInfo(
        hostname="TEST-UNKNOWN",
        vendor="Cisco",
        model="TEST",
        os_version="UNKNOWN",
        role="core",

        # Important:
        ipv6_supported=None,
        ipv6_routing_enabled=None,

        interfaces=[],

        routing=IPv6Routing(
            enabled=None,
            route_count=0,
            connected_routes=0,
            local_routes=0,
            static_routes=0,
            ospfv3=False,
            ripng=False,
            eigrpv6=False,
            bgp_ipv6=False,
        ),
    )


device = create_unknown_device()

result = assess_ipv6(device)

print("\n" + "=" * 60)
print("UNKNOWN TEST")
print("=" * 60)

print(
    f"Device: {result['device']}"
)

if result["score"] is None:
    print("Score: N/A")
else:
    print(f"Score: {result['score']}%")

print(
    f"Readiness: {result['readiness']}"
)

for finding in result["findings"]:

    print(
        f"[{finding['status']}] "
        f"{finding['id']} - "
        f"{finding['name']}"
    )

    print(
        f"    {finding['message']}"
    )


ipv6_routing_result = next(
    finding
    for finding in result["findings"]
    if finding["id"] == "IPV6-04"
)


assert (
    ipv6_routing_result["status"]
    == "UNKNOWN"
)

print("\n[PASS] IPV6-04 UNKNOWN validation")