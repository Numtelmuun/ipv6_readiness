from netmiko import ConnectHandler


device = {
    "device_type": "cisco_ios",
    "host": "10.3.132.31",
    "username": "cisco",
    "password": "cisco",
}

print("Connecting to R1...")

connection = ConnectHandler(**device)

print("Connected successfully!")

print("\n===== SHOW VERSION =====")
print(connection.send_command("show version"))

print("\n===== SHOW IP INTERFACE BRIEF =====")
print(connection.send_command("show ip interface brief"))

print("\n===== SHOW IPV6 INTERFACE BRIEF =====")
print(connection.send_command("show ipv6 interface brief"))

connection.disconnect()

print("\nConnection closed.")