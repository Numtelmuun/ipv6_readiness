import yaml

from network.ssh_client import NetworkDevice


def load_devices():

    with open(
        "config/devices.yaml",
        "r",
        encoding="utf-8"
    ) as file:

        data = yaml.safe_load(file)

    devices = []

    for item in data["devices"]:

        device = NetworkDevice(
            name=item["name"],
            host=item["host"],
            platform=item["platform"],
            username=item["username"],
            password=item["password"],
            role=item.get("role"),
        )

        devices.append(device)

    return devices