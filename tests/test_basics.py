import os
import unittest
from app import external_css, server, app_name, app


class TestApp(unittest.TestCase):

    def test_font_awesome_in_external_css(self):
        css = list(filter(lambda x: 'font-awesome.min.css' in x, external_css))
        self.assertIs(len(css), 1)

    def test_root_layout_is_container(self):
        self.assertIs(app._layout.className, 'container')

    def test_secret_key_is_set(self):
        # don't forget to set the SECRET_KEY on TravisCI too
        self.assertNotEquals(os.environ.get('SECRET_KEY'), 'secret-key')

    def test_server_is_named_after_app_name(self):
        self.assertIs(server.name, app_name)


if __name__ == '__main__':
    unittest.main()
