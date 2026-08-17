from vendors.base.adapter import VendorAdapter
from vendors.cisco.adapter import CiscoAdapter


_ADAPTERS: dict[str, type[VendorAdapter]] = {
    "cisco_ios": CiscoAdapter,
}


def get_vendor_adapter(
    platform: str
) -> VendorAdapter:

    adapter_class = _ADAPTERS.get(platform)

    if adapter_class is None:
        raise ValueError(
            f"Unsupported vendor platform: {platform}"
        )

    return adapter_class()