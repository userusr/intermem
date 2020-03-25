#!/usr/bin/env python
"""Testing dummy memcached module."""
import os
import unittest

from intermem.client import Client


class TestIntermem(unittest.TestCase):
    """Test client."""
    @unittest.skipIf(os.getenv('MEMCACHED_HOST') is None,
                     'Define "MEMCACHED_HOST" to test real connection')
    def test_real_connection(self):
        """Test connection to real memcached server."""
        host = os.getenv('MEMCACHED_HOST')
        client = Client(host)
        self.assertEqual(client.sock.getpeername()[0], host)
        self.assertEqual(client.sock.getpeername()[1], 11211)
        client.close()
