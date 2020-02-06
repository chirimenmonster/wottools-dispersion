
import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from lib import translate as tr


class GettextTestCase(unittest.TestCase):

    def test_gettext_translate(self):
        gettext = tr.Gettext(localedir='test/data/res')
        self.assertEqual('T-34', gettext.translate('#ussr_vehicles:T-34'))

    def test_gettext_translate_failurepattern(self):
        gettext = tr.Gettext(localedir='test/data/res')
        self.assertEqual('missing', gettext.translate('#ussr_vehicles:missing'))
        self.assertEqual('#missing:T-34', gettext.translate('#missing:T-34'))
        gettext.localedir = 'missing'
        self.assertEqual('#ussr_vehicles:T-34', gettext.translate('#ussr_vehicles:T-34'))


class TranslateTestCase(unittest.TestCase):

    def test_transalte(self):
        tr.config.BASE_DIR = 'test/data'
        self.assertEqual('T-34', tr.g_translate('#ussr_vehicles:T-34'))
        self.assertEqual('missing', tr.g_translate('#ussr_vehicles:missing'))
        self.assertEqual('#missing:T-34', tr.g_translate('#missing:T-34'))


class ApplicationTranslateTestCase(unittest.TestCase):

    def test_transalte(self):
        from lib.config import g_config as config
        from lib.application import g_application as app
        config.GUI_DIR = 'test/data/res'
        config.scriptspkg = 'test/data/res/packages/scripts.pkg'
        config.schema = 'test/data/itemschema.json'
        config.localedir = 'test/data/res'
        app.setup(config)
        self.assertEqual('T-34', app.gettext.translate('#ussr_vehicles:T-34'))


if __name__ == '__main__':
    unittest.main()
