from network.inventory import load_devices


devices = load_devices()

for device in devices:

    print("\n" + "=" * 60)
    print(f"DEVICE: {device.name}")
    print("=" * 60)

    print("\n--- SHOW VERSION ---")
    print(device.execute("show version"))

    print("\n--- IPV6 INTERFACE BRIEF ---")
    print(
        device.execute(
            "show ipv6 interface brief"
        )
    )

    print("\n--- IPV6 ROUTING ---")
    print(
        device.execute(
            "show ipv6 route"
        )
    )

    print("\n--- IPV6 PROTOCOLS ---")
    print(
        device.execute(
            "show ipv6 protocols"
        )
    )

    print("\n--- IPV6 INTERFACE FastEthernet0/1 ---")
    print(
        device.execute(
            "show ipv6 interface FastEthernet0/1"
        )
    )