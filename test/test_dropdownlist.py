
import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from lib.config import g_config as config
from lib.application import g_application as app
from lib.dropdownlist import DropdownList


class DropdownListTestCase(unittest.TestCase):

    def setUp(self):
        config.GUI_DIR = 'test/data/res'
        config.scriptspkg = 'test/data/res/packages/scripts.pkg'
        config.schema = 'test/data/itemschema.json'
        config.localedir = 'test/data/res'
        config.outputjson = True
        app.setup(config)
        self.dropdownlist = DropdownList()

    def test_fetchNationList(self):
        result = self.dropdownlist.fetchNationList()
        self.assertEqual(11, len(result))
        self.assertEqual([['germany', 'GERMANY'], ['ussr', 'USSR'], ['usa', 'USA'], ['japan', 'JAPAN'], ['china', 'CHINA'], ['uk', 'UK'], ['france', 'FRANCE'], ['czech', 'CZECH'], ['poland', 'POLAND'], ['italy', 'ITALY'], ['sweden', 'SWEDEN']], result)
        
    def test_fetchTierList(self):
        result = self.dropdownlist.fetchTierList()
        self.assertEqual(10, len(result))
        self.assertEqual([['1', 'I'], ['2', 'II'], ['3', 'III'], ['4', 'IV'], ['5', 'V'], ['6', 'VI'], ['7', 'VII'], ['8', 'VIII'], ['9', 'IX'], ['10', 'X']], result)

    def test_fetchTypeList(self):
        result = self.dropdownlist.fetchTypeList()
        self.assertEqual(5, len(result))
        self.assertEqual([['LT', 'LT'], ['MT', 'MT'], ['HT', 'HT'], ['TD', 'TD'], ['SPG', 'SPG']], result)

    def test_fetchVehicleList(self):
        ctx = {'nation':'germany', 'tier':str(10), 'type':'HT'}
        self.assertEqual(None, self.dropdownlist.fetchVehicleList(param=ctx))
