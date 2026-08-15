from network.inventory import load_devices


devices = load_devices()

for device in devices:

    print(
        f"{device.name} "
        f"{device.host} "
        f"{device.platform}"
    )