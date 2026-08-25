from vendors.base.adapter import VendorAdapter
from vendors.cisco.adapter import CiscoAdapter
from vendors.juniper.adapter import JuniperAdapter
from vendors.huawei.adapter import HuaweiAdapter


_ADAPTERS: dict[str, type[VendorAdapter]] = {
    "cisco_ios": CiscoAdapter,
    "cisco_xe": CiscoAdapter,
    "cisco": CiscoAdapter,
    "juniper_junos": JuniperAdapter,
    "juniper": JuniperAdapter,
    "huawei_vrp": HuaweiAdapter,
    "huawei": HuaweiAdapter,
}


def get_vendor_adapter(platform_or_vendor: str) -> VendorAdapter:

    adapter_class = _ADAPTERS.get(platform_or_vendor.lower())

    if adapter_class is None:
        raise ValueError(
            f"Unsupported vendor platform: {platform_or_vendor}"
        )

    return adapter_class()
