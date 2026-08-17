from abc import ABC, abstractmethod


class NetworkTransport(ABC):

    @abstractmethod
    def execute(
        self,
        commands: list[str]
    ) -> dict[str, str]:
        """
        Execute commands on a network device.

        Returns:
            Dictionary mapping command -> output.
        """
        raise NotImplementedError