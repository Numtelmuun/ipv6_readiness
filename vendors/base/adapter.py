from abc import ABC, abstractmethod

from models.device import DeviceInfo


class VendorAdapter(ABC):
    """Collect vendor CLI data and normalize it into :class:`DeviceInfo`.

    Adapters own commands and parsing only. The assessment engine consumes the
    resulting vendor-neutral model and has no vendor-specific branches.
    """

    vendor: str

    @abstractmethod
    def get_commands(self) -> list[str]:
        """Return operational commands needed for IPv6 assessment."""
        raise NotImplementedError

    def get_device_info_commands(self) -> list[str]:
        return self.get_commands()[:1]

    def get_ipv6_interface_commands(self) -> list[str]:
        return self.get_commands()[1:2]

    def get_ipv6_route_commands(self) -> list[str]:
        return self.get_commands()[2:3]

    def get_ipv6_protocol_commands(self) -> list[str]:
        return self.get_commands()[3:4]

    @abstractmethod
    def parse_outputs(self, outputs: dict[str, str]) -> DeviceInfo:
        """Normalize command output without network transport concerns."""
        raise NotImplementedError

    @abstractmethod
    def parse_hostname(self, outputs: dict[str, str]) -> str | None:
        """Return a hostname when one is present in collected output."""
        raise NotImplementedError
