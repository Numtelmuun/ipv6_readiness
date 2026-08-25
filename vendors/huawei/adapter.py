from vendors.base.adapter import VendorAdapter
from vendors.huawei.commands import (
    ASSESSMENT_COMMANDS,
    BGP_IPV6,
    IPV6_INTERFACES,
    OSPFV3,
)
from vendors.huawei.parser import parse_device_data, parse_hostname


class HuaweiAdapter(VendorAdapter):
    vendor = "Huawei"

    def get_commands(self) -> list[str]:
        return ASSESSMENT_COMMANDS.copy()

    def get_ipv6_interface_commands(self) -> list[str]:
        return [IPV6_INTERFACES]

    def get_ipv6_protocol_commands(self) -> list[str]:
        return [OSPFV3, BGP_IPV6]

    def parse_outputs(self, outputs: dict[str, str]):
        return parse_device_data(outputs)

    def parse_hostname(self, outputs: dict[str, str]) -> str | None:
        return parse_hostname(
            outputs.get("display current-configuration | include sysname", "")
        )
