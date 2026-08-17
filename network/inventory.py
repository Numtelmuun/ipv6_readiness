import yaml

from network.ssh_client import NetworkDevice
from vendors.registry import get_vendor_adapter


def load_devices():

    with open(
        "config/devices.yaml",
        "r",
        encoding="utf-8"
    ) as file:

        data = yaml.safe_load(file)

    devices = []

    for item in data["devices"]:

        adapter = get_vendor_adapter(
            item["platform"]
        )

        device = NetworkDevice(
            name=item["name"],
            host=item["host"],
            platform=item["platform"],
            username=item["username"],
            password=item["password"],
            role=item.get("role"),
            adapter=adapter,
        )

        devices.append(device)

    return devices