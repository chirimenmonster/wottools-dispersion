
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
        self.assertEqual([['germany', 'GERMANY'], ['ussr', 'USSR'], ['usa', 'USA'], ['japan', 'JAPAN'],
            ['china', 'CHINA'], ['uk', 'UK'], ['france', 'FRANCE'], ['czech', 'CZECH'], ['poland', 'POLAND'],
            ['italy', 'ITALY'], ['sweden', 'SWEDEN']], result)
        
    def test_fetchTierList(self):
        result = self.dropdownlist.fetchTierList()
        self.assertEqual(10, len(result))
        self.assertEqual([['1', 'I'], ['2', 'II'], ['3', 'III'], ['4', 'IV'], ['5', 'V'], ['6', 'VI'],
            ['7', 'VII'], ['8', 'VIII'], ['9', 'IX'], ['10', 'X']], result)

    def test_fetchTypeList(self):
        result = self.dropdownlist.fetchTypeList()
        self.assertEqual(5, len(result))
        self.assertEqual([['LT', 'LT'], ['MT', 'MT'], ['HT', 'HT'], ['TD', 'TD'], ['SPG', 'SPG']], result)

    def test_fetchVehicleList(self):
        ctx = {'nation':'ussr', 'tier':str(10), 'type':'HT'}
        expectdata = [
            ['R90_IS_4M', 'IS-4'],
            ['R45_IS-7', 'IS-7'],
            ['R145_Object_705_A', 'Object 705A'],
            ['R155_Object_277', 'Object 277'],
            ['R169_ST_II', 'ST-II'],
            ['R110_Object_260', 'Object 260'],
            ['R157_Object_279R', 'Object 279 early']]
        self.assertEqual(expectdata, self.dropdownlist.fetchVehicleList(param=ctx))

    def test_fetchModuleList(self):
        ctx = {'vehicle':'R19_IS-3', 'chassis':'IS-3M', 'turret':'Mod_T-10', 'engine':'V-2-54IS', 'radio':'R113',
            'gun':'_122mm_BL-9', 'shell':'_122mm_UBR-471P'}
        expect_chassis = [
            ['IS-3', 'IS-3'],
            ['IS-3M', 'IS-3M']]
        expect_turret = [
            ['IS-3', 'Kirovets-1'],
            ['Mod_T-10', 'IS-3']]
        expect_engine = [
            ['V-11', 'V-11'],
            ['V-2-54IS', 'V-2-54IS']]
        expect_radio = [
            ['_10RK', '10RK'],
            ['_12RT', '12RT'],
            ['R113', 'R-113']]
        expect_gun = [
            ['_122-mm_D-25T_with_a_piston_shutter', '122 mm D-2-5T'],
            ['_122-mm_D-25T_with_wedges_shutter', '122 mm D-25T'],
            ['_122mm_BL-9', '122 mm BL-9']]
        expect_shell = [
            ['_122mm_UBR-471', 'AP: UBR-471'],
            ['_122mm_UBR-471P', 'APCR: BR-471D'],
            ['_122mm_UOF-471', 'HE: UOF-471']]
        self.assertEqual(expect_chassis, self.dropdownlist.fetchChassisList(param=ctx))
        self.assertEqual(expect_turret, self.dropdownlist.fetchTurretList(param=ctx))
        self.assertEqual(expect_engine, self.dropdownlist.fetchEngineList(param=ctx))
        self.assertEqual(expect_radio, self.dropdownlist.fetchRadioList(param=ctx))
        self.assertEqual(expect_gun, self.dropdownlist.fetchGunList(param=ctx))
        self.assertEqual(expect_shell, self.dropdownlist.fetchShellList(param=ctx))
        result = self.dropdownlist.fetchGunList(param=ctx)

    def test_application(self):
        self.assertEqual('T-34', app.gettext.translate('#ussr_vehicles:T-34'))
