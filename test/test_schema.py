
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
        with open('test/data/itemschema.json', 'r') as fp:
            self.schema = json.load(fp)
        self.ctx = {'nation':'ussr', 'vehicle':'R04_T-34', 'chassis':'T-34_mod_1943', 'turret':'T-34_mod_1942',
            'engine':'V-2-34', 'fueltank':'Average', 'radio':'_9RM', 'gun':'_76mm_S-54', 'shell':'_76mm_UBR-354MP'}
        self.resource = vp.Resource(self.strage, self.vpath, self.schema)
    
    def test_schema(self):
        self.assertEqual(['germany', 'ussr', 'usa', 'japan', 'china', 'uk', 'france', 'czech', 'poland', 'italy', 'sweden'], self.resource.getValue('settings:nationsOrder'))
        self.assertEqual(735.5, self.resource.getValue('physics:hpToWatts'))
        self.assertEqual('ussr', self.resource.getValue('vehicle:nation', self.ctx))
        self.assertEqual(29390.0, self.resource.getValue('vehicle:totalWeight', self.ctx))        
        self.assertEqual(12.51275944198707, self.resource.getValue('vehicle:powerWeightRatioSI', self.ctx))
        self.assertEqual(14.016600510789694, self.resource.getValue('vehicle:maxSpeed_medium', self.ctx))
        self.assertEqual([16.565073330933274, 14.016600510789694, 7.922426375663741], self.resource.getValue('vehicle:maxSpeed', self.ctx))
        self.assertEqual(['Observer', 'R04_T-34', 'R02_SU-85', 'R01_IS', 'R03_BT-7'], self.resource.getValue('vehicle:list', self.ctx))
        self.assertEqual('R04_T-34', self.resource.getValue('vehicle:index', self.ctx))
        self.assertEqual('0', self.resource.getValue('vehicle:id', self.ctx))
        self.assertEqual('T-34', self.resource.getValue('vehicle:userString', self.ctx))
        self.assertEqual('T-34', self.resource.getValue('vehicle:shortUserString', self.ctx))
        self.assertEqual('T-34', self.resource.getValue('vehicle:displayString', self.ctx))
        self.assertEqual('', self.resource.getValue('vehicle:secret', self.ctx))
        self.assertEqual('', self.resource.getValue('vehicle:siegeMode', self.ctx))
        self.assertEqual('MT', self.resource.getValue('vehicle:type', self.ctx))
        self.assertEqual(['T-34_mod_1941', 'T-34_mod_1943'], self.resource.getValue('vehicle:chassis', self.ctx))
        self.assertEqual(['T-34_mod_1940', 'T-34_mod_1942'], self.resource.getValue('vehicle:turrets', self.ctx))
        self.assertEqual(['V-2', 'V-2-34'], self.resource.getValue('vehicle:engines', self.ctx))
        self.assertEqual(['Average'], self.resource.getValue('vehicle:fueltanks', self.ctx))
        self.assertEqual('Average', self.resource.getValue('vehicle:fueltank', self.ctx))
        self.assertEqual(['_9R', '_9RM'], self.resource.getValue('vehicle:radios', self.ctx))
        self.assertEqual('15000', self.resource.getValue('hull:weight', self.ctx))
        self.assertEqual('T-34_mod_1943', self.resource.getValue('chassis:index', self.ctx))
        self.assertEqual('T-34_mod_1942', self.resource.getValue('turret:index', self.ctx))
        self.assertEqual('V-2-34', self.resource.getValue('engine:index', self.ctx))
        self.assertEqual('203', self.resource.getValue('fueltank:id', self.ctx))
        self.assertEqual('_76mm_S-54', self.resource.getValue('gun:index', self.ctx))
        self.assertEqual('_76mm_UBR-354MP', self.resource.getValue('shell:index', self.ctx))
        self.assertEqual(['_76mm_L-11', '_76mm_F-34', '_57mm_ZiS-4', '_76mm_S-54'], self.resource.getValue('turret:guns', self.ctx))
        self.assertEqual('2040 386', self.resource.getValue('engine:rpmRange', self.ctx))
        self.assertEqual('V', self.resource.getValue('gun:tier', self.ctx))
        self.assertEqual('5.7', self.resource.getValue('gun:reloadTime', self.ctx))
        self.assertEqual(['_76mm_UBR-354MA', '_76mm_UBR-354MP', '_76mm_UOF-354M'], self.resource.getValue('gun:shots', self.ctx))
        self.assertEqual('APCR', self.resource.getValue('shell:kindShort', self.ctx))
        self.assertEqual('125', self.resource.getValue('shot:piercingPower_1', self.ctx))
        self.assertEqual('125 156 39', self.resource.getValue('shot:piercingPower', self.ctx))
        self.assertEqual('156', self.resource.getValue('shell:piercingPower', self.ctx))
