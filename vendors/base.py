from abc import ABC, abstractmethod

from models.device import DeviceInfo


class VendorAdapter(ABC):
    """
    Common interface for all network vendors.

    A vendor adapter is responsible for:
    1. Providing vendor-specific commands
    2. Normalizing vendor-specific CLI output
       into the common DeviceInfo model
    """

    vendor: str = "Unknown"

    @abstractmethod
    def get_commands(self) -> list[str]:
        """
        Return the commands required for IPv6 assessment.
        """
        raise NotImplementedError

    @abstractmethod
    def parse(
        self,
        outputs: dict[str, str],
    ) -> DeviceInfo:
        """
        Convert vendor-specific command output
        into the common DeviceInfo model.
        """
        raise NotImplementedError