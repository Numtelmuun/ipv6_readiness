from abc import ABC, abstractmethod

from models.device import (
    DeviceInfo,
    IPv6Interface,
    IPv6Routing,
)


class VendorParser(ABC):
    """
    Base interface for vendor-specific parsers.

    Every vendor parser must normalize its device output
    into the common DeviceInfo data model.
    """

    vendor: str = "Unknown"

    @abstractmethod
    def parse_version(self, output: str) -> DeviceInfo:
        """
        Parse device version/model information.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_ipv6_interfaces(
        self,
        output: str,
    ) -> list[IPv6Interface]:
        """
        Parse IPv6 interface information.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_ipv6_routes(
        self,
        output: str,
    ) -> IPv6Routing:
        """
        Parse IPv6 routing information.
        """
        raise NotImplementedError

    @abstractmethod
    def parse_ipv6_protocols(
        self,
        output: str,
        routing: IPv6Routing,
    ) -> IPv6Routing:
        """
        Parse IPv6 routing protocol information.
        """
        raise NotImplementedError

    def parse_device_data(
        self,
        version_output: str,
        interface_output: str,
        routing_output: str,
        protocols_output: str,
    ) -> DeviceInfo:
        """
        Normalize all vendor-specific outputs into DeviceInfo.
        """

        device = self.parse_version(
            version_output
        )

        device.interfaces = self.parse_ipv6_interfaces(
            interface_output
        )

        device.routing = self.parse_ipv6_routes(
            routing_output
        )

        device.routing = self.parse_ipv6_protocols(
            protocols_output,
            device.routing,
        )

        device.ipv6_routing_enabled = (
            device.routing.enabled
        )

        return device