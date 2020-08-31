from flask import Flask

import server
from server.tests.base_test_config import BaseTestCase


class TestFlaskApp(BaseTestCase):
    def test_create_app_must_exists(self):
        self.assertEqual(hasattr(server, "create_app"), True)

    def test_create_app_must_be_callable(self):
        self.assertEqual(hasattr(server.create_app, "__call__"), True)

    def test_create_app_must_return_flask_app(self):
        self.assertIsInstance(server.create_app(), Flask)
