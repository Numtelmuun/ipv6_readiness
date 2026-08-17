from abc import ABC, abstractmethod


class VendorAdapter(ABC):

    vendor: str

    @abstractmethod
    def get_commands(self) -> list[str]:
        pass

    @abstractmethod
    def parse_outputs(self, outputs):
        pass

    @abstractmethod
    def parse_hostname(self, outputs) -> str | None:
        pass