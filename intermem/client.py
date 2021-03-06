"""Dummy memcached client library."""
import socket
from typing import List, Optional

RECV_SIZE = 4096


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
        self.sock = None  # type: Optional[socket.socket]

    def connect(self) -> None:
        """Socket connect."""
        self.close()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.connect((self.host, self.port))
        except Exception:
            sock.close()
            raise

        self.sock = sock

    def close(self) -> None:
        """Close socket."""
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    def cmd_set(self,
                key: bytes,
                value: bytes,
                data_flags: bytes = b'0',
                expire: bytes = b'0') -> bool:
        r"""Store data command.

        Format of memcached command:
            <command name> <key> <flags> <exptime> <bytes> [noreply]\r\n

        :param key: key
        :type key: bytes
        :param value: value
        :type value: bytes
        :param data_flags: flags must be non greater than 16-bit unsigned
                           integer (65535 in decimal), defaults to b'0'
        :type data_flags: bytes, optional
        :param expire: 0 - the item never expires
                       Unix time or offset (sec)
                       negative value - the item is immediately expired
                       defaults to b'0'
        :type expire: bytes, optional
        :return: True if item is stored
        :rtype: bool
        """
        result = False
        cmd = self._cmd_store(b'set', key, value, data_flags, expire)

        self._check_flags(data_flags)

        if self.sock is None:
            self.connect()

        self.sock.sendall(cmd)

        line = self._readlines()[0]
        if line == b'STORED':
            result = True

        return result

    def cmd_get(self, key: bytes) -> Optional[bytes]:
        """Get data command.

        :param key: key
        :type key: bytes
        :return: None if key does not exists, or value
        :rtype: Optional[bytes]
        """
        cmd = self._cmd_recv(b'get', key)

        if self.sock is None:
            self.connect()

        self.sock.sendall(cmd)

        lines = self._readlines()
        if lines[0].startswith(b'END'):
            return None
        elif lines[0].startswith(b'VALUE'):
            return lines[1]

    def cmd_delete(self, key: bytes) -> bool:
        """Command "delete".

        :param key: key
        :type key: bytes
        :return: True if key deleted, False if key was not found
        :rtype: bool
        """
        cmd = self._cmd_maint(b'delete', key)

        if self.sock is None:
            self.connect()

        self.sock.sendall(cmd)

        line = self._readlines()[0]
        if line.startswith(b'DELETED'):
            return True
        else:
            return False

    def _check_flags(self, flags: bytes) -> None:
        int_flags = int(flags)
        if int_flags > 2**16 or int_flags < 0:
            raise ValueError(
                f'Flags mast be 16-bit unsigned integer, got: {flags}')

    def _readlines(self, length: int = RECV_SIZE) -> List[bytes]:
        lines = []
        sep = b'\r\n'

        buf = self.sock.recv(length)

        while buf.find(sep) != -1:
            right, _, left = buf.partition(sep)
            buf = left
            lines.append(right)

        return lines

    def _cmd_store(self, name: bytes, key: bytes, value: bytes,
                   data_flags: bytes, expire: bytes) -> bytes:
        return b' '.join([
            name,
            key,
            data_flags,
            expire,
            bytes(str(len(value)), 'ascii'),
        ]) + b'\r\n' + value + b'\r\n'

    def _cmd_recv(self, name: bytes, key: bytes) -> bytes:
        return b' '.join([
            name,
            key,
        ]) + b'\r\n'

    def _cmd_maint(self, name: bytes, key: bytes) -> bytes:
        return b' '.join([
            name,
            key,
        ]) + b'\r\n'
