
import unittest

from lib import translate as tr

from lib.config import Config
from lib.application import Application


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


class ApplicationTranslateTestCase(unittest.TestCase):

    def setUp(self):
        config = Config()
        config.localedir = 'test/data/res'
        config.pkgdir = 'test/data/res/packages'
        self.app = Application()
        self.app.setup(config)

    def test_transalte(self):
        self.assertEqual('T-34', self.app.gettext.translate('#ussr_vehicles:T-34'))


if __name__ == '__main__':
    unittest.main()
