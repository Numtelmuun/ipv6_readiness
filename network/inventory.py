import yaml

from network.ssh_client import NetworkDevice
from vendors.registry import get_vendor_adapter


def load_devices(inventory_path: str = "config/devices.yaml"):

    with open(
        inventory_path,
        "r",
        encoding="utf-8"
    ) as file:

        data = yaml.safe_load(file)

    devices = []

    for item in data["devices"]:

        adapter = get_vendor_adapter(
            item.get("vendor") or item["platform"]
        )

        device = NetworkDevice(
            name=item["name"],
            host=item["host"],
            platform=item["platform"],
            username=item["username"],
            password=item["password"],
            role=item.get("role"),
            adapter=adapter,
            device_type=item.get("device_type", "unknown"),
            required_ipv6_interfaces=item.get("required_ipv6_interfaces"),
            required_routing_protocols=item.get("required_routing_protocols", []),
            supported_routing_protocols=item.get("supported_routing_protocols"),
        )

        devices.append(device)

    return devices
