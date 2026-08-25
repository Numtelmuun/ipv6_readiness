from vendors.base.adapter import VendorAdapter
from vendors.juniper.commands import (
    ASSESSMENT_COMMANDS,
    BGP,
    INTERFACES_DETAIL,
    INTERFACES_TERSE,
    IPV6_ROUTES,
    OSPFV3,
)
from vendors.juniper.parser import parse_device_data, parse_version


class JuniperAdapter(VendorAdapter):
    vendor = "Juniper"

    def get_commands(self) -> list[str]:
        return ASSESSMENT_COMMANDS.copy()

    def get_ipv6_interface_commands(self) -> list[str]:
        return [INTERFACES_TERSE, INTERFACES_DETAIL]

    def get_ipv6_protocol_commands(self) -> list[str]:
        return [OSPFV3, BGP]

    def get_ipv6_route_commands(self) -> list[str]:
        return [IPV6_ROUTES]

    def parse_outputs(self, outputs: dict[str, str]):
        return parse_device_data(outputs)

    def parse_hostname(self, outputs: dict[str, str]) -> str | None:
        return parse_version(outputs.get("show version", "")).hostname
