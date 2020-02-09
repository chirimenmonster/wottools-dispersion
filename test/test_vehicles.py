
import os
import sys
import unittest
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from lib.vpath import Strage, VPath, Settings, Resource
from lib.vehicles import VehicleDatabase, VehicleSpec, ModuleSpec
from lib.translate import Gettext

class VehicleTestCase(unittest.TestCase):

    def setUp(self):
        strage = Strage()
        vpath = VPath(scriptsdir='../wot.scripts', guidir='test/data/res')
        schema = Settings(schema='res/itemschema.json').schema
        gettext = Gettext(localedir='test/data/res')
        resource = Resource(strage, vpath, schema)
        resource.gettext = gettext
        self.vd = VehicleDatabase(resource)
        self.vd.prepare()

    def test_getVehicleCtx(self):
        self.assertEqual(646, len(self.vd.getVehicleCtx()))
        self.assertEqual(789, len(self.vd.getVehicleCtx(VehicleSpec(secrets=[True, False]))))
        self.assertEqual(143, len(self.vd.getVehicleCtx(VehicleSpec(secrets=[True]))))
        self.assertEqual(30, len(self.vd.getVehicleCtx(VehicleSpec(nations=['germany'], tiers=[8]))))
        self.assertEqual(8, len(self.vd.getVehicleCtx(VehicleSpec(nations=['germany'], tiers=[8], types=['TD']))))

    def test_getModuleList(self):
        ctx = self.vd.getCtx('R04_T-34')
        self.assertEqual(['T-34_mod_1940', 'T-34_mod_1942'], self.vd.getModuleList('turret', ctx))
        ctx = {'nation':'ussr', 'id':21, 'vehicle':'R19_IS-3', 'tier':8, 'type':'HT', 'secret':False,
            'chassis':'miss', 'turret':'miss', 'engine':'miss', 'radio':'miss', 'gun':'miss', 'shell':'miss'}
        self.assertEqual(['IS-3', 'IS-3M'], self.vd.getModuleList('chassis', ctx))


    def test_getVehicleItems(self):
        ctx = self.vd.getCtx('R04_T-34')
        ctx['turret'] = 'T-34_mod_1942'
        self.assertEqual({'vehicle:userString':'T-34', 'turret:index':'T-34_mod_1942'}, self.vd.getVehicleItems(['vehicle:userString', 'turret:index'], ctx))

    def test_getModuleCtx(self):
        self.assertEqual(168, len(self.vd.getModuleCtx('R04_T-34')))
        self.assertEqual(1, len(self.vd.getModuleCtx('R04_T-34', ModuleSpec())))
        self.assertEqual(2, len(self.vd.getModuleCtx('R04_T-34', ModuleSpec(chassis=None))))
        self.assertEqual(2, len(self.vd.getModuleCtx('R04_T-34', ModuleSpec(turret=None))))
        self.assertEqual(2, len(self.vd.getModuleCtx('R04_T-34', ModuleSpec(engine=None))))
        self.assertEqual(2, len(self.vd.getModuleCtx('R04_T-34', ModuleSpec(radio=None))))
        self.assertEqual(7, len(self.vd.getModuleCtx('R04_T-34', ModuleSpec(turret=None, gun=None))))
        self.assertEqual(3, len(self.vd.getModuleCtx('R04_T-34', ModuleSpec(turret=0, gun=None))))
        self.assertEqual(4, len(self.vd.getModuleCtx('R04_T-34', ModuleSpec(turret=1, gun=None))))
        self.assertEqual(4, len(self.vd.getModuleCtx('R04_T-34', ModuleSpec(turret=-1, gun=None))))
        self.assertEqual(3, len(self.vd.getModuleCtx('R04_T-34', ModuleSpec(turret=0, gun=0, shell=None))))
        self.assertEqual(3, len(self.vd.getModuleCtx('R04_T-34', ModuleSpec(turret=0, gun=1, shell=None))))
        self.assertEqual(3, len(self.vd.getModuleCtx('R04_T-34', ModuleSpec(turret=0, gun=2, shell=None))))
        self.assertEqual(3, len(self.vd.getModuleCtx('R04_T-34', ModuleSpec(turret=1, gun=0, shell=None))))
        self.assertEqual(3, len(self.vd.getModuleCtx('R04_T-34', ModuleSpec(turret=1, gun=1, shell=None))))
        self.assertEqual(3, len(self.vd.getModuleCtx('R04_T-34', ModuleSpec(turret=1, gun=2, shell=None))))
        self.assertEqual(3, len(self.vd.getModuleCtx('R04_T-34', ModuleSpec(turret=1, gun=3, shell=None))))

    def test_getVehicleModuleCtx(self):
        self.assertEqual(47298, len(self.vd.getVehicleModuleCtx()))
        self.assertEqual(5, len(self.vd.getVehicleModuleCtx(VehicleSpec(nations=['germany'], tiers=[1]))))
        vehicleSpec = VehicleSpec(nations=['germany'], types=['LT'], secrets=[True])
        moduleSpec= ModuleSpec()
        self.assertEqual(7, len(self.vd.getVehicleModuleCtx(vehicleSpec, moduleSpec)))
        
    def test_getModuleCtx_List(self):
        moduleSpec = ModuleSpec(chassis='IS-3M', turret='Mod_T-10', engine='V-2-54IS', radio='R113',
            gun='_122mm_BL-9', shell='_122mm_UBR-471P')
        expect = {'nation': 'ussr', 'id': 21, 'vehicle': 'R19_IS-3', 'tier': 8, 'type': 'HT', 'secret': False,
            'chassis': 'IS-3M', 'turret': 'Mod_T-10', 'engine': 'V-2-54IS', 'radio': 'R113',
            'gun': '_122mm_BL-9', 'shell': '_122mm_UBR-471P'}
        result = self.vd.getModuleCtx('R19_IS-3', moduleSpec)
        self.assertEqual(expect, result[0])
        
        self.assertEqual({'shell:explosionRadius': None}, self.vd.getVehicleItems(['shell:explosionRadius'], result[0]))
        moduleSpec = moduleSpec._replace(shell='_122mm_UOF-471')
        result = self.vd.getModuleCtx('R19_IS-3', moduleSpec)
        self.assertEqual({'shell:explosionRadius': '2.49'}, self.vd.getVehicleItems(['shell:explosionRadius'], result[0]))

    