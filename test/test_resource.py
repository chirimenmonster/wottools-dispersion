
import os
import sys
import unittest
import json
import xml.etree.ElementTree as ET

from lib.config import g_config as config
from lib.application import g_application as app, Settings
from lib.translate import Gettext
from lib.vpath import VPath, Strage
from lib.resource import Resource


class ResourceTestCase(unittest.TestCase):

    def setUp(self):
        config.GUI_DIR = 'test/data/res'
        config.scriptsdir = 'test/data/res'
        config.schema = 'res/itemschema.json'
        config.localedir = 'test/data/res'
        app.setup(config)
        self.resource = app.resource
        self.param = {'nation':'ussr', 'vehicle':'R04_T-34', 'chassis':'T-34_mod_1943', 'turret':'T-34_mod_1942',
            'engine':'V-2-34', 'radio':'_9RM', 'gun':'_76mm_S-54'}
        return

    def test_resource_substitute(self):
        result = self.resource.substitute('vehicles/{nation}/list.xml', {'nation':'ussr'})
        self.assertEqual('vehicles/ussr/list.xml', result)
        with self.assertRaises(KeyError):
            result = self.resource.substitute('vehicles/{nation}/list.xml', {})
        result = self.resource.substitute('vehicles/{nation}/list.xml', {'nation':'ussr'})
        self.assertEqual('vehicles/ussr/list.xml', result)
        result = self.resource.substitute('vehicles/{nation}/{vehicle}.xml', {'nation':'ussr', 'vehicle':'R04_T34'})
        self.assertEqual('vehicles/ussr/R04_T34.xml', result)

    def test_resource_getFromFile(self):
        return
        result = self.resource.getFromFile('vehicles/ussr/list.xml', 'R04_T-34/userString')
        self.assertEqual('#ussr_vehicles:T-34', result[0])
        result = self.resource.getFromFile('vehicles/ussr/list.xml', 'R04_T-34/missing')
        self.assertEqual(0, len(result))
        with self.assertRaises(FileNotFoundError):
            result = self.resource.getFromFile('vehicles/ussr/missing', 'R04_T-34/userString')
            
    def test_resource_getNodes_resources(self):
        resources = [{'file':'gui/gui_settings.xml', 'xpath':'settings/[name="nations_order"]/value/item'}]
        result = self.resource.getNodes(resources=resources)
        self.assertIsInstance(result, list)
        self.assertIn('ussr', result)
                   
    def test_resource_getNodes_immediateValue_list(self):
        return
        resources = [{'file':'gui/gui_settings.xml', 'xpath':'missing'}, {'immediate':['germany', 'ussr', 'usa', 'uk']}]
        result = self.resource.getNodes(resources=resources)
        self.assertIsInstance(result, list)
        self.assertEqual(['germany', 'ussr', 'usa', 'uk'], result)
        result = self.resource.getValue(ctx=self.param, resources=resources, type='list', order=['ussr', 'germany', 'uk'])
        self.assertEqual(['ussr', 'germany', 'uk', 'usa'], result)
        
    def test_resource_getNodes_immediateValue_string(self):
        self.assertEqual('ussr', self.resource.getValue('vehicle:nation', self.param))
        self.assertEqual(735.5, self.resource.getValue('physics:hpToWatts', self.param))

    def test_resource_getNodes_func_sum(self):
        weight = {'hull:weight': 15000, 'chassis:weight':8000, 'turret:weight':3900, 'engine:weight':750,
            'fueltank:weight':250, 'radio:weight':100, 'gun:weight':1390 }
        for m,w in weight.items():
            result = self.resource.getValue(m, self.param)
            self.assertEqual(str(w), result)
        result = self.resource.getValue('vehicle:totalWeight', self.param)
        self.assertEqual(29390.0, result)

    def test_resource_getNodes_func_div(self):
        result = self.resource.getValue('engine:power', self.param)
        result = self.resource.getValue('vehicle:totalWeight', self.param)
        self.assertEqual(0.01701258931609391, self.resource.getValue('vehicle:powerWeightRatio', self.param))
        self.assertEqual(14.016600510789694, self.resource.getValue('vehicle:maxSpeed_medium', self.param))

    def test_resource_getNodes_func_mul(self):
        result = self.resource.getValue('vehicle:powerWeightRatioSI', self.param)
        self.assertEqual(12.51275944198707, result)

    def test_resource_getNodes_func_join(self):
        result = self.resource.getValue('vehicle:maxSpeed', self.param)
        self.assertEqual([16.565073330933274, 14.016600510789694, 7.922426375663741], result)

    def test_resource_getValue_1(self):
        return
        self.assertEqual('T-34', self.resource.getValue('vehicle:shortUserString', self.param))

    def test_resource_getValue_2(self):
        return
        resources = [{'file':'vehicles/{nation}/list.xml', 'xpath':'name(*)'}]
        result = self.resource.getValue(ctx=self.param, resources=resources, type='list')
        self.assertEqual(['Observer', 'R04_T-34', 'R02_SU-85', 'R01_IS', 'R03_BT-7'], result)

    def test_resource_getValue_3(self):
        resources = [{'file':'vehicles/{nation}/list.xml', 'xpath':'position(R04_T-34)'}]
        result = self.resource.getValue(ctx=self.param, resources=resources, type='int')
        self.assertEqual(2, result)

    def test_resource_getValue_4(self):
        result = self.resource.getValue('settings:tiersLabel')
        expect = {'1':'I', '2':'II', '3':'III', '4':'IV', '5': 'V',
                    '6':'VI', '7':'VII', '8':'VIII', '9':'IX', '10':'X' }
        self.assertEqual(expect, result)


    def test_resource_convert(self):
        value = ['Observer', 'R04_T-34', 'R02_SU-85']
        self.assertEqual('R04_T-34', self.resource.convert(value[1:2]))
        self.assertEqual('Observer R04_T-34 R02_SU-85', self.resource.convert(value))
        self.assertEqual(['Observer', 'R04_T-34', 'R02_SU-85'], self.resource.convert(value, 'list'))


    def test_resource_assingMap(self):
        dictmap = {'lightTank': 'LT', 'mediumTank': 'MT', 'heavyTank': 'HT'}
        self.assertEqual('MT', self.resource.assignMap('mediumTank', dictmap))
        self.assertEqual('MT HT', self.resource.assignMap(' unknown mediumTank unknown heavyTank secret ', dictmap))

    def test_resource_assingMap_gettext(self):
        self.assertEqual('T-34', self.resource.assignMap('#ussr_vehicles:T-34', 'gettext()'))

    def test_resource_assingMap_split(self):
        self.assertEqual(['1.1', '1.3', '2.3'], self.resource.assignMap('1.1 1.3 2.3', 'split()'))
            

if __name__ == '__main__':
    unittest.main()
    