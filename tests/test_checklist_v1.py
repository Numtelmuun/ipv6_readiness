from assessment.engine import assess_ipv6
from models.device import DeviceInfo, IPv6Interface, IPv6Routing


def capable(**overrides):
    values = dict(hostname="fixture", device_type="router", ipv6_supported=True,
                  ipv6_addressing_capable=True, ipv6_forwarding_capable=True,
                  ipv6_routing_table_capable=True, ipv6_routing_enabled=True,
                  required_ipv6_interfaces=["Gi0/0"], required_routing_protocols=[],
                  supported_routing_protocols=["ospfv3", "bgp_ipv6"],
                  interfaces=[IPv6Interface("Gi0/0", operational=True, ipv6_enabled=True,
                                            link_local="fe80::1")],
                  routing=IPv6Routing(enabled=True, connected_routes=1))
    values.update(overrides)
    return DeviceInfo(**values)


def by_id(result, check_id):
    return next(f for f in result["findings"] if f["id"] == check_id)


def test_scenario_a_ready_and_provenance():
    result = assess_ipv6(capable())
    assert result["readiness"] == "READY"
    assert result["score"] == 100
    assert result["checklist"] == {
        "name": "IPv6 Readiness Checklist", "version": "1.0", "basis": "RIPE-772",
        "scope": "Basic IPv6 deployment capability and configuration readiness",
        "full_ripe_772_compliance": False,
    }


def test_scenario_b_configuration_required_not_replacement():
    device = capable(ipv6_routing_enabled=False,
                     interfaces=[IPv6Interface("Gi0/0", ipv6_enabled=False)])
    result = assess_ipv6(device)
    assert result["readiness"] == "CONFIGURATION_REQUIRED"
    assert by_id(result, "IPV6-01")["status"] == "PASS"
    assert by_id(result, "IPV6-02")["status"] == "PASS"
    assert by_id(result, "IPV6-05")["remediation"] == "CONFIGURE"
    assert any(f["remediation"] == "CONFIGURE" for f in result["findings"])


def test_scenario_c_upgrade_or_replace_required():
    result = assess_ipv6(capable(ipv6_supported=False))
    assert result["readiness"] == "UPGRADE_OR_REPLACE_REQUIRED"
    assert by_id(result, "IPV6-01")["failure_kind"] == "capability_unsupported"


def test_scenario_d_insufficient_data():
    result = assess_ipv6(DeviceInfo(hostname="unknown", required_routing_protocols=[]))
    assert result["readiness"] == "INSUFFICIENT_DATA"
    assert result["score"] is None
    assert by_id(result, "IPV6-01")["status"] == "UNKNOWN"


def test_scenario_e_conditional_routing():
    core = assess_ipv6(capable(required_routing_protocols=["ospfv3"]))
    edge = assess_ipv6(capable(required_routing_protocols=[]))
    assert by_id(core, "IPV6-07")["status"] == "FAIL"
    assert by_id(core, "IPV6-07")["remediation"] == "CONFIGURE"
    assert core["readiness"] == "CONFIGURATION_REQUIRED"
    assert by_id(edge, "IPV6-07")["status"] == "NOT_APPLICABLE"
    assert by_id(edge, "IPV6-07")["max_score"] == 5
    assert edge["score"] == 100


def test_known_unconfigured_required_interface_is_failure():
    device = capable(required_ipv6_interfaces=["Gi0/0", "Gi0/1"], interfaces=[
        IPv6Interface("Gi0/0", operational=True, ipv6_enabled=True, link_local="fe80::1"),
        IPv6Interface("Gi0/1", ipv6_enabled=False),
    ])
    result = assess_ipv6(device)
    assert by_id(result, "IPV6-09")["status"] == "FAIL"
    assert result["readiness"] == "CONFIGURATION_REQUIRED"


def test_ipv6_configured_required_interface_down_is_warning():
    device = capable(interfaces=[
        IPv6Interface("Gi0/0", operational=False, ipv6_enabled=True,
                      link_local="fe80::1", global_addresses=["2001:db8::1/64"]),
    ])
    result = assess_ipv6(device)
    finding = by_id(result, "IPV6-09")
    assert finding["status"] == "WARNING"
    assert finding["category"] == "CONFIGURATION"
    assert finding["remediation"] == "VERIFY"
    assert "IPv6-configured but operationally down" in finding["message"]
    assert finding["evidence"] == ["Gi0/0"]
    assert result["readiness"] == "CONFIGURATION_REQUIRED"
    recommendation = next(r for r in result["recommendations"] if r["id"] == "IPV6-09")
    assert recommendation["remediation"] == "VERIFY"
    assert recommendation["recommendation"] == (
        "Verify the required interface operational state and link condition."
    )
    assert "Collect or verify the evidence" not in recommendation["recommendation"]


def test_nonempty_global_address_is_not_required_to_prove_addressing_capability():
    result = assess_ipv6(capable())
    assert not result["device"] is None
    assert by_id(result, "IPV6-02")["status"] == "PASS"
