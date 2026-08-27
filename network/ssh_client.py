from netmiko import ConnectHandler


class NetworkDevice:

    def __init__(
        self,
        name: str,
        host: str,
        platform: str,
        username: str,
        password: str,
        role: str | None = None,
        adapter=None,
        device_type: str = "unknown",
        required_ipv6_interfaces: list[str] | None = None,
        required_routing_protocols: list[str] | None = None,
        supported_routing_protocols: list[str] | None = None,
    ):
        self.name = name
        self.host = host
        self.platform = platform
        self.username = username
        self.password = password
        self.role = role
        self.adapter = adapter
        self.device_type = device_type
        self.required_ipv6_interfaces = required_ipv6_interfaces
        self.required_routing_protocols = required_routing_protocols or []
        self.supported_routing_protocols = supported_routing_protocols

    def _connection_params(self):

        return {
            "device_type": self.platform,
            "host": self.host,
            "username": self.username,
            "password": self.password,
        }

    def execute(self, command: str) -> str:

        connection = ConnectHandler(
            **self._connection_params()
        )

        try:
            return connection.send_command(command)

        finally:
            connection.disconnect()

    def execute_many(
        self,
        commands: list[str]
    ) -> dict[str, str]:

        connection = ConnectHandler(
            **self._connection_params()
        )

        try:

            results = {}

            for command in commands:

                results[command] = connection.send_command(
                    command
                )

            return results

        finally:
            connection.disconnect()
