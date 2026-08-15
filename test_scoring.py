from network.inventory import load_devices
from parsers.cisco_parser import parse_ipv6_device_data
from assessment.engine import assess_ipv6


EXPECTED = {
    "R1": {
        "score": 100.0,
        "readiness": "READY",
    },
    "R2": {
        "score": 0.0,
        "readiness": "NOT_READY",
    },
    "R3": {
        "score": 90.0,
        "readiness": "READY",
    },
}


def collect_and_assess(device):

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

    return assess_ipv6(normalized)


devices = load_devices()

all_passed = True


for device in devices:

    if device.name not in EXPECTED:
        continue

    print(
        f"\nTesting {device.name}..."
    )

    result = collect_and_assess(device)

    expected = EXPECTED[device.name]

    score_ok = (
        result["score"]
        == expected["score"]
    )

    readiness_ok = (
        result["readiness"]
        == expected["readiness"]
    )

    print(
        f"  Expected score: "
        f"{expected['score']}"
    )

    print(
        f"  Actual score:   "
        f"{result['score']}"
    )

    print(
        f"  Expected readiness: "
        f"{expected['readiness']}"
    )

    print(
        f"  Actual readiness:   "
        f"{result['readiness']}"
    )

    if score_ok and readiness_ok:

        print("  [PASS]")

    else:

        print("  [FAIL]")
        all_passed = False


print("\n" + "=" * 60)

if all_passed:
    print("SCORING VALIDATION: PASS")
else:
    print("SCORING VALIDATION: FAIL")