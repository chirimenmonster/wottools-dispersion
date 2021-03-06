
import unittest

from lib.config import Config
from lib.application import Application
from lib.itemmap import MapFactory


class MapFactoryTestCase(unittest.TestCase):

    def setUp(self):
        config = Config()
        config.guipkg = 'test/data/res/packages/gui.pkg'
        config.scriptspkg = 'test/data/res/packages/scripts.pkg'
        config.schema = 'res/itemschema.json'
        config.localedir = 'test/data/res'
        app = Application()
        app.setup(config)
        self.factory = MapFactory(app)

    def test_MapDict(self):
        desc = {
            "lightTank": "LT", "mediumTank": "MT", "heavyTank": "HT",
            "AT-SPG": "TD", "SPG": "SPG"
        }
        itemmap = self.factory.create(desc)
        result = itemmap.getValue(' other words mediumTank and AT-SPG etc. ')
        self.assertEqual('MT TD', result)

    def test_MapDict(self):
        desc = "gettext()"
        itemmap = self.factory.create(desc)
        result = itemmap.getValue('#ussr_vehicles:T-34')
        self.assertEqual('T-34', result)

    def test_MapSplit(self):
        desc = "split()"
        itemmap = self.factory.create(desc)
        result = itemmap.getValue('This sentence consists of several words')
        self.assertEqual(['This', 'sentence', 'consists', 'of', 'several', 'words'], result)

    def test_MapSplit(self):
        desc = "split()[2]"
        itemmap = self.factory.create(desc)
        result = itemmap.getValue('This sentence consists of several words')
        self.assertEqual('consists', result)

    def test_MapRoman(self):
        desc = "roman()"
        itemmap = self.factory.create(desc)
        result = itemmap.getValue('7')
        self.assertEqual('VII', result)
