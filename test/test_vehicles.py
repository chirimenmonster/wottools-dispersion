
import os
import sys
import unittest
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from lib.vpath import Strage, VPath, Settings, Resource
from lib.vehicles import VehicleDatabase, VehicleSpec, ModuleSpec
from lib.translate import g_gettext

class VehicleTestCase(unittest.TestCase):

    def setUp(self):
        strage = Strage()
        vpath = VPath(scriptsdir='../wot.scripts', guidir='test/data/res')
        schema = Settings(schema='test/data/itemschema.json').schema
        resource = Resource(strage, vpath, schema)
        self.vd = VehicleDatabase(resource)
        self.vd.prepare()
        if g_gettext.localedir is None:
            g_gettext.localedir = 'test/data/res'

    def test_getVehicleCtx(self):
        self.assertEqual(642, len(self.vd.getVehicleCtx()))
        self.assertEqual(778, len(self.vd.getVehicleCtx(VehicleSpec(secrets=[True, False]))))
        self.assertEqual(136, len(self.vd.getVehicleCtx(VehicleSpec(secrets=[True]))))
        self.assertEqual(30, len(self.vd.getVehicleCtx(VehicleSpec(nations=['germany'], tiers=[8]))))
        self.assertEqual(8, len(self.vd.getVehicleCtx(VehicleSpec(nations=['germany'], tiers=[8], types=['TD']))))

    def test_getModuleList(self):
        ctx = self.vd.getCtx('R04_T-34')
        self.assertEqual(['T-34_mod_1940', 'T-34_mod_1942'], self.vd.getModuleList('turret', ctx))

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
        self.assertEqual(47076, len(self.vd.getVehicleModuleCtx()))
        self.assertEqual(5, len(self.vd.getVehicleModuleCtx(VehicleSpec(nations=['germany'], tiers=[1]))))
    