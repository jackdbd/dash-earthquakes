import os
import unittest
from app import server, app_name, app


class TestApp(unittest.TestCase):
    def test_root_layout_is_container(self):
        self.assertIs(app._layout.className, "container")

    def test_secret_key_is_set(self):
        # don't forget to set the SECRET_KEY on TravisCI too
        self.assertNotEqual(os.environ.get("SECRET_KEY"), "secret-key")

    def test_server_is_named_after_app_name(self):
        self.assertIs(server.name, app_name)


if __name__ == "__main__":
    unittest.main()
