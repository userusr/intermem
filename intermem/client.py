"""Dummy memcached client library."""
import socket


class Client():
    """A simple client to memcached database for interview perposes."""
    def __init__(self, host: str = '127.0.0.1', port: int = 11211) -> None:
        """Constructor.

        :param host: IP address or host name, defaults to '127.0.0.1'
        :type host: str, optional
        :param port: TCP port, defaults to 11211
        :type port: int, optional
        """
        self.host = host
        self.port = port
        self.sock = None
        self._connect()

    def _connect(self):
        self.close()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((self.host, self.port))
        except Exception:
            sock.close()
            raise

        self.sock = sock

    def close(self):
        """Close socket."""
        if self.sock is not None:
            self.sock.close()
            self.sock = None
