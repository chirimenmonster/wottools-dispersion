
import unittest

from lib.config import Config
from lib.application import Application


class ApplicationTestCase(unittest.TestCase):

    def test_application(self):
        config = Config()
        config.guipkg = 'test/data/res/packages/gui.pkg'
        config.scriptspkg = 'test/data/res/packages/scripts.pkg'
        config.localedir = 'test/data/res'
        app = Application()
        vpath = app.setupVPath(config)
        result = vpath.getPathInfo('gui/gui_settings.xml')
        self.assertEqual('gui/gui_settings.xml', result.path)
        self.assertEqual('test/data/res/packages/gui.pkg', result.pkg)

    def test_setupGettext(self):
        config = Config()
        config.localedir = 'missing'
        app = Application()
        self.assertRaises(FileNotFoundError, app.setupGettext, config)

    def test_setupSettings(self):
        config = Config()
        config.schema = 'missing'
        app = Application()
        self.assertRaisesRegex(FileNotFoundError, r'not found schema file: ', app.setupSettings, config)

if __name__ == '__main__':
    unittest.main()
    