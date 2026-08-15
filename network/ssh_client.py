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
    ):
        self.name = name
        self.host = host
        self.platform = platform
        self.username = username
        self.password = password
        self.role = role

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

    def execute_many(self, commands: list[str]) -> dict[str, str]:

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