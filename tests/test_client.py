#!/usr/bin/env python
"""Testing dummy memcached module."""
import functools
import os
import unittest
from typing import Tuple  # noqa
from unittest import mock

from intermem.client import Client


class MockSocket():
    """Mock socket class."""
    def __init__(self, client: Client) -> None:
        """Constructor.

        :param client: Client class
        :type client: Client
        """
        self.client = client

    def close(self) -> None:
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
        client.close()

    def test_mock_socket(self) -> None:
        """Connect to mock socket."""
        client = Client()
        sock = MockSocket(client)
        client.connect = mock.Mock(
            side_effect=functools.partial(setattr, client, 'sock', sock))
        client.connect()
        self.assertEqual(client.sock.getpeername()[0], client.host)
        self.assertEqual(client.sock.getpeername()[1], client.port)
        client.close()
