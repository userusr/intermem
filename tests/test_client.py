#!/usr/bin/env python
"""Testing dummy memcached module."""
import functools
import os
import unittest
from typing import List, Tuple, Optional  # noqa
from unittest import mock

from intermem.client import Client


class MockSocket():
    """Mock socket class."""
    def __init__(self,
                 client: Client,
                 recv_buf: Optional[bytes] = None) -> None:
        """Constructor.

        :param client: Client class
        :type client: Client
        """
        self.client = client
        self.recv_buf = recv_buf

    def recv(self, length: int) -> bytes:
        """Mosc recv method of socket."""
        return self.recv_buf

    def close(self) -> None:
        """Mock."""
        pass

    def sendall(self, _: bytes) -> None:
        """Mock."""
        pass

    def getpeername(self) -> Tuple[str, int]:
        """Mock of getpeername function.

        :return: tuple of server and port
        :rtype: Tuple[str, int]
        """
        return (self.client.host, self.client.port)


class TestIntermem(unittest.TestCase):
    """Test client."""
    @unittest.skipIf(
        os.getenv('MEMCACHED_HOST') is None,
        'Define "MEMCACHED_HOST" to test real connection')
    def test_real_connection(self) -> None:
        """Test connection to real memcached server."""
        host = os.getenv('MEMCACHED_HOST')
        client = Client(host)
        client.connect()
        self.assertEqual(client.sock.getpeername()[0], host)
        self.assertEqual(client.sock.getpeername()[1], 11211)

        self.assertTrue(client.cmd_set(b'key', b'value'))
        self.assertTrue(client.cmd_set(b'key1', b'value1'))

        self.assertEqual(client.cmd_get(b'key'), b'value')
        self.assertEqual(client.cmd_get(b'key1'), b'value1')

        self.assertIsNone(client.cmd_get(b'key_unknown'))
        self.assertTrue(client.cmd_delete(b'key'))
        self.assertFalse(client.cmd_delete(b'key_unknown'))

        client.close()

    def test_cmd_store(self) -> None:
        """Test generation of store command."""
        client = Client()
        cmd = client._cmd_store(b'name', b'key', b'value', b'10', b'8')
        self.assertEqual(cmd, b'name key 10 8 5\r\nvalue\r\n')

    def test_cmd_recv(self) -> None:
        """Test generation of recive command."""
        client = Client()
        cmd = client._cmd_recv(b'name', b'key')
        self.assertEqual(cmd, b'name key\r\n')

    def test_cmd_maint(self) -> None:
        """Test generation of delete command."""
        client = Client()
        cmd = client._cmd_maint(b'name', b'key')
        self.assertEqual(cmd, b'name key\r\n')

    def test_readlines_from_socket(self) -> None:
        """Test readline from socket."""
        client = self._get_mock_client(b'STORED\r\n')
        lines = client._readlines()
        self.assertListEqual(lines, [b'STORED'])

    def test_cmd_set(self) -> None:
        """Test set command."""
        client = self._get_mock_client(b'STORED\r\n')
        stored = client.cmd_set(b'key', b'value')
        self.assertTrue(stored)

        client = self._get_mock_client(b'ERROR\r\n')
        stored = client.cmd_set(b'key', b'value')
        self.assertFalse(stored)

    def test_cmd_get(self) -> None:
        """Test get command."""
        client = self._get_mock_client(b'VALUE key 0 5\r\nvalue\r\nEND\r\n')
        self.assertEqual(client.cmd_get(b'key1'), b'value')

        client = self._get_mock_client(b'END\r\n')
        self.assertIsNone(client.cmd_get(b'key_unknown'))

    def test_cmd_delete(self) -> None:
        """Test delete command."""
        client = self._get_mock_client(b'DELETED\r\n')
        self.assertTrue(client.cmd_delete(b'key1'))

        client = self._get_mock_client(b'ERROR\r\n')
        self.assertFalse(client.cmd_delete(b'key_unknown'))

    def test_mock_socket(self) -> None:
        """Connect to mock socket."""
        client = self._get_mock_client()
        self.assertEqual(client.sock.getpeername()[0], client.host)
        self.assertEqual(client.sock.getpeername()[1], client.port)
        client.close()

    def _get_mock_client(self, recv_buf: Optional[bytes] = None) -> Client:
        client = Client()
        sock = MockSocket(client, recv_buf)
        client.connect = mock.Mock(
            side_effect=functools.partial(setattr, client, 'sock', sock))
        client.connect()
        return client
