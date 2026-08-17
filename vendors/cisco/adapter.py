from vendors.base.adapter import VendorAdapter

from vendors.cisco.parser import (
    parse_ipv6_device_data,
    parse_hostname,
)


class CiscoAdapter(VendorAdapter):

    vendor = "Cisco"

    def get_commands(self) -> list[str]:

        return [
            "show version",
            "show ipv6 interface brief",
            "show ipv6 route",
            "show ipv6 protocols",
            "show running-config | include ^hostname",
        ]

    def parse_outputs(self, outputs):

        return parse_ipv6_device_data(
            version_output=outputs[
                "show version"
            ],
            interface_output=outputs[
                "show ipv6 interface brief"
            ],
            routing_output=outputs[
                "show ipv6 route"
            ],
            protocols_output=outputs[
                "show ipv6 protocols"
            ],
        )

    def parse_hostname(self, outputs):

        return parse_hostname(
            outputs.get(
                "show running-config | include ^hostname",
                ""
            )
        )