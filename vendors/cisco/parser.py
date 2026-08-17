from models.device import DeviceInfo
from parsers.cisco_parser import (
    parse_ipv6_device_data,
    parse_hostname,
)


class CiscoParser:

    def parse(self, outputs: dict[str, str]) -> DeviceInfo:

        device = parse_ipv6_device_data(
            version_output=outputs.get(
                "show version",
                ""
            ),
            interface_output=outputs.get(
                "show ipv6 interface brief",
                ""
            ),
            routing_output=outputs.get(
                "show ipv6 route",
                ""
            ),
            protocols_output=outputs.get(
                "show ipv6 protocols",
                ""
            ),
        )

        hostname = parse_hostname(
            outputs.get(
                "show running-config | include ^hostname",
                ""
            )
        )

        if hostname:
            device.hostname = hostname

        return device