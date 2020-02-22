
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
        self.assertEqual('gui.pkg', result.pkg)

if __name__ == '__main__':
    unittest.main()
    