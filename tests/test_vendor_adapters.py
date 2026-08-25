from pathlib import Path

from assessment.engine import assess_ipv6
from network.inventory import load_devices
from vendors.cisco.adapter import CiscoAdapter
from vendors.base import VendorAdapter
from vendors.huawei.adapter import HuaweiAdapter
from vendors.huawei.parser import parse_device_data as parse_huawei
from vendors.juniper.adapter import JuniperAdapter
from vendors.juniper.parser import parse_device_data as parse_juniper
from vendors.registry import get_vendor_adapter


FIXTURES = Path(__file__).parent / "fixtures"


def fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def cisco_outputs() -> dict[str, str]:
    return {
        "show version": fixture("cisco_show_version.txt"),
        "show ipv6 interface brief": fixture("cisco_ipv6_interfaces.txt"),
        "show ipv6 route": fixture("cisco_ipv6_routes.txt"),
        "show ipv6 protocols": fixture("cisco_ipv6_protocols.txt"),
        "show running-config | include ^hostname": "hostname R1\n",
    }


def juniper_outputs() -> dict[str, str]:
    return {
        "show version": fixture("juniper_show_version.txt"),
        "show interfaces terse": fixture("juniper_interfaces_terse.txt"),
        "show interfaces detail": fixture("juniper_interfaces_detail.txt"),
        "show route table inet6.0": fixture("juniper_ipv6_routes.txt"),
        "show ospf3 overview": fixture("juniper_ospf3.txt"),
        "show bgp summary": fixture("juniper_bgp.txt"),
    }


def huawei_outputs() -> dict[str, str]:
    return {
        "display version": fixture("huawei_display_version.txt"),
        "display ipv6 interface": fixture("huawei_ipv6_interfaces.txt"),
        "display ipv6 routing-table": fixture("huawei_ipv6_routes.txt"),
        "display ospfv3 peer": fixture("huawei_ospfv3.txt"),
        "display bgp ipv6 routing-table": fixture("huawei_bgp_ipv6.txt"),
        "display current-configuration | include sysname": "sysname R3\n",
    }


def test_vendor_registry_and_inventory_select_adapters_without_connecting():
    adapters = [
        get_vendor_adapter("cisco"),
        get_vendor_adapter("juniper_junos"),
        get_vendor_adapter("huawei"),
    ]
    assert isinstance(adapters[0], CiscoAdapter)
    assert isinstance(adapters[1], JuniperAdapter)
    assert isinstance(adapters[2], HuaweiAdapter)
    assert all(isinstance(adapter, VendorAdapter) for adapter in adapters)

    devices = load_devices(str(FIXTURES / "mixed_vendors.yaml"))
    assert [device.name for device in devices] == ["R1", "R2", "R3", "SW1"]
    assert [device.adapter.vendor for device in devices] == [
        "Cisco", "Juniper", "Huawei", "Cisco"
    ]


def test_juniper_parser_normalizes_ipv6_data_and_protocols():
    device = parse_juniper(juniper_outputs())

    assert (device.vendor, device.hostname, device.model) == ("Juniper", "R2", "mx204")
    assert device.ipv6_supported is True
    assert device.ipv6_routing_enabled is True
    assert len(device.interfaces) == 2
    assert device.interfaces[0].global_addresses == ["2001:db8:20::1/64"]
    assert device.interfaces[0].link_local == "fe80::20/64"
    assert device.routing.ospfv3 is True
    assert device.routing.bgp_ipv6 is True
    assert "OSPFv3" in device.routing.ipv6_protocols


def test_huawei_parser_normalizes_ipv6_data_and_protocols():
    device = parse_huawei(huawei_outputs())

    assert (device.vendor, device.model, device.os_version) == ("Huawei", "AR1220", "8.180")
    assert device.hostname == "R3"
    assert device.ipv6_supported is True
    assert device.ipv6_routing_enabled is True
    assert len(device.interfaces) == 2
    assert device.interfaces[0].global_addresses == ["2001:DB8:30::1/64"]
    assert device.interfaces[0].link_local == "FE80::30"
    assert device.routing.ospfv3 is True
    assert device.routing.bgp_ipv6 is True


def test_unknown_routing_state_remains_unknown():
    device = parse_juniper({"show version": fixture("juniper_show_version.txt")})

    assert device.ipv6_routing_enabled is None
    assert device.routing.enabled is None


def test_mixed_vendor_normalized_devices_use_same_deterministic_engine():
    cisco = CiscoAdapter().parse_outputs(cisco_outputs())
    cisco.hostname, cisco.role = "R1", "edge"
    switch = CiscoAdapter().parse_outputs(cisco_outputs())
    switch.hostname, switch.role = "SW1", "access"
    juniper = JuniperAdapter().parse_outputs(juniper_outputs())
    juniper.role = "core"
    huawei = HuaweiAdapter().parse_outputs(huawei_outputs())
    huawei.role = "core"

    results = [assess_ipv6(device) for device in (cisco, juniper, huawei, switch)]

    assert [result["device"] for result in results] == ["R1", "R2", "R3", "SW1"]
    assert [result["vendor"] for result in results] == ["Cisco", "Juniper", "Huawei", "Cisco"]
    assert all(len(result["findings"]) == 9 for result in results)
    assert all(result["readiness"] != "INSUFFICIENT_DATA" for result in results)
