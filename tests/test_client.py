#!/usr/bin/env python
"""Testing dummy memcached module."""
import unittest

from intermem.client import Client


class TestIntermem(unittest.TestCase):
    """Client class."""
    def test_client(self):
        """Dummy test."""
        assert isinstance(Client(), Client)
