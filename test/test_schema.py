
import os
import sys
import unittest
import json
import xml.etree.ElementTree as ET

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from lib import vpath as vp
from lib import translate as tr

class SchemaTestCase(unittest.TestCase):

    def setUp(self):
        tr.g_gettext.localedir = 'test/data/res'
        self.strage = vp.Strage()
        self.vpath = vp.VPath(scriptsdir='test/data/res', guidir='test/data/res')
        with open('test/itemschema.json', 'r') as fp:
            self.schema = json.load(fp)
        param = {'nation':'ussr', 'vehicle':'R04_T-34', 'chassis':'T-34_mod_1943', 'turret':'T-34_mod_1942',
            'engine':'V-2-34', 'fueltank':'Average', 'radio':'_9RM', 'gun':'_76mm_S-54'}
        self.resource = vp.Resource(self.strage, self.vpath, self.schema, param)
    
    def test_schema(self):
        self.assertEqual(['germany', 'ussr', 'usa'], self.resource.getValue('settings:nationsOrder'))
        self.assertEqual(735.5, self.resource.getValue('physics:hpToWatts'))
        self.assertEqual('ussr', self.resource.getValue('vehicle:nation'))
        self.assertEqual(29390.0, self.resource.getValue('vehicle:totalWeight'))        
        self.assertEqual(12.51275944198707, self.resource.getValue('vehicle:powerWeightRatioSI'))
        self.assertEqual(14.016600510789694, self.resource.getValue('vehicle:maxSpeed_medium'))
        self.assertEqual([16.565073330933274, 14.016600510789694, 7.922426375663741], self.resource.getValue('vehicle:maxSpeed'))
        self.assertEqual(['Observer', 'R04_T-34', 'R02_SU-85', 'R01_IS', 'R03_BT-7'], self.resource.getValue('vehicle:list'))
        self.assertEqual('R04_T-34', self.resource.getValue('vehicle:index'))
        self.assertEqual('0', self.resource.getValue('vehicle:id'))
        self.assertEqual('T-34', self.resource.getValue('vehicle:userString'))
        self.assertEqual('T-34', self.resource.getValue('vehicle:shortUserString'))
        self.assertEqual('T-34', self.resource.getValue('vehicle:displayString'))
        self.assertEqual('', self.resource.getValue('vehicle:secret'))
        self.assertEqual('', self.resource.getValue('vehicle:siegeMode'))
        self.assertEqual('MT', self.resource.getValue('vehicle:type'))
        self.assertEqual(['T-34_mod_1941', 'T-34_mod_1943'], self.resource.getValue('vehicle:chassis'))
        self.assertEqual(['T-34_mod_1940', 'T-34_mod_1942'], self.resource.getValue('vehicle:turrets'))
        self.assertEqual(['V-2', 'V-2-34'], self.resource.getValue('vehicle:engines'))
        self.assertEqual(['Average'], self.resource.getValue('vehicle:fueltanks'))
        self.assertEqual('Average', self.resource.getValue('vehicle:fueltank'))
        self.assertEqual(['_9R', '_9RM'], self.resource.getValue('vehicle:radios'))
        self.assertEqual('15000', self.resource.getValue('hull:weight'))
        self.assertEqual('T-34_mod_1943', self.resource.getValue('chassis:index'))
        self.assertEqual('T-34_mod_1942', self.resource.getValue('turret:index'))
        self.assertEqual('V-2-34', self.resource.getValue('engine:index'))
        self.assertEqual('203', self.resource.getValue('fueltank:id'))
        self.assertEqual(['_76mm_L-11', '_76mm_F-34', '_57mm_ZiS-4', '_76mm_S-54'], self.resource.getValue('turret:guns'))
