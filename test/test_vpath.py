
import os
import sys
import unittest
import json
import xml.etree.ElementTree as ET

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from lib import vpath as vp


class VPathTestCase(unittest.TestCase):

    def test_vpath_getPathInfo(self):
        vpath = vp.VPath(pkgdir='c:/Games/World_of_Tanks_ASIA/res/packages')
        self.assertEqual(vp.PathInfo(
            pkg='c:/Games/World_of_Tanks_ASIA/res/packages/scripts.pkg',
            path='scripts/item_defs/vehicles/ussr/list.xml'
        ), vpath.getPathInfo('vehicles/ussr/list.xml'))
        self.assertEqual(vp.PathInfo(
            pkg='c:/Games/World_of_Tanks_ASIA/res/packages/gui.pkg',
            path='gui/gui_settings.xml'
        ), vpath.getPathInfo('gui/gui_settings.xml'))

    def test_vpath_scriptsdir(self):
        vpath = vp.VPath(pkgdir='c:/Games/World_of_Tanks_ASIA/res/packages', scriptsdir='d:/git/wot.scripts')
        self.assertEqual(vp.PathInfo(
            path='d:/git/wot.scripts/scripts/item_defs/vehicles/ussr/list.xml'
        ), vpath.getPathInfo('vehicles/ussr/list.xml'))
        self.assertEqual(vp.PathInfo(
            pkg='c:/Games/World_of_Tanks_ASIA/res/packages/gui.pkg',
            path='gui/gui_settings.xml'
        ), vpath.getPathInfo('gui/gui_settings.xml'))

    def test_vpath_guidir(self):
        vpath = vp.VPath(pkgdir='c:/Games/World_of_Tanks_ASIA/res/packages', guidir='./test')
        self.assertEqual(vp.PathInfo(
            pkg='c:/Games/World_of_Tanks_ASIA/res/packages/scripts.pkg',
            path='scripts/item_defs/vehicles/ussr/list.xml'
        ), vpath.getPathInfo('vehicles/ussr/list.xml'))
        self.assertEqual(vp.PathInfo(
            path='./test/gui/gui_settings.xml'
        ), vpath.getPathInfo('gui/gui_settings.xml'))


class StrageTestCase(unittest.TestCase):

    def test_strage_readStream(self):
        file = 'test/data/res/gui/gui_settings.xml'
        strage = vp.Strage()
        with open(file, 'rb') as fp:
            data = fp.read()
        self.assertEqual(data, strage.readStream(file).read())
        with self.assertRaises(FileNotFoundError):
            strage.readStream('missing')
        with self.assertRaises(KeyError):
            strage.readStream('missing', 'test/data/empty.zip')
        with self.assertRaises(FileNotFoundError):
            strage.readStream('missing', 'test/data/missing.zip')

    def test_strage_readData(self):
        file = 'test/data/res/gui/gui_settings.xml'
        strage = vp.Strage()
        with open(file, 'rb') as fp:
            data = fp.read()
        self.assertFalse(strage.isCachedData(file))
        self.assertEqual(data, strage.readData(file))
        self.assertTrue(strage.isCachedData(file))
        self.assertEqual(data, strage.readData(file))


    def test_vpath_readXml(self):
        file = 'test/data/res/gui/gui_settings.xml'
        strage = vp.Strage()
        with open(file, 'rb') as fp:
            data = ET.tostring(ET.fromstring(fp.read()), encoding='utf-8')
        self.assertFalse(strage.isCachedXml(file))
        self.assertEqual(data, ET.tostring(strage.readXml(file), encoding='utf-8'))
        self.assertTrue(strage.isCachedXml(file))
        with self.assertRaises(FileNotFoundError):
            strage.readXml('missing.xml')
        with self.assertRaises(KeyError):
            strage.readXml('missing', 'test/data/empty.zip')
        element = strage.readXml('test/data/badnamespace.xml')
        self.assertEqual('#usa_vehicles:T14', element.find('A21_T14/userString').text)


class ElementTestCase(unittest.TestCase):

    def setUp(self):
        vpath = vp.VPath(scriptsdir='test/data/res')
        path = vpath.getPathInfo('vehicles/ussr/list.xml')
        strage = vp.Strage()
        root = strage.readXml(path)
        self.element = vp.Element(root)

    def test_element_findText(self):
        self.assertEqual('#ussr_vehicles:T-34', self.element.findText('R04_T-34/userString'))
        self.assertIsNone(self.element.findText('R04_T-34/missing'))

    def test_element_findNodename(self):
        self.assertEqual('R04_T-34', self.element.findNodename('R04_T-34'))
        self.assertIsNone(self.element.findNodename('missing'))

    def test_element_findNodelist(self):
        result = self.element.findNodelist('*')
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], vp.Element)
        self.assertEqual('R04_T-34', result[1].tag)
        result = self.element.findNodelist('missing')
        self.assertIsInstance(result, list)
        self.assertEqual(0, len(result))


class ResourceTestCase(unittest.TestCase):

    def setUp(self):
        self.strage = vp.Strage()
        self.vpath = vp.VPath(scriptsdir='test/data/res', guidir='test/data/res')
        with open('test/data/itemschema.json', 'r') as fp:
            self.schema = json.load(fp)
        self.param = {'nation':'ussr', 'vehicle':'R04_T-34', 'chassis':'T-34_mod_1943', 'turret':'T-34_mod_1942',
            'engine':'V-2-34', 'radio':'_9RM', 'gun':'_76mm_S-54'}
        self.resource = vp.Resource(self.strage, self.vpath, self.schema, self.param)

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
        result = self.resource.getFromFile('vehicles/ussr/list.xml', 'R04_T-34/userString')
        self.assertEqual('#ussr_vehicles:T-34', result[0])
        result = self.resource.getFromFile('vehicles/ussr/list.xml', 'R04_T-34/missing')
        self.assertEqual(0, len(result))
        with self.assertRaises(FileNotFoundError):
            result = self.resource.getFromFile('vehicles/ussr/missing', 'R04_T-34/userString')
    
    def test_resource_getValue(self):
        result = self.resource.getValue('vehicle:userString', self.param)
        self.assertEqual(1, len(result))
        self.assertEqual('#ussr_vehicles:T-34', result[0])
        
    def test_resource_getNodes_resources(self):
        resources = [{'file':'gui/gui_settings.xml', 'xpath':'settings/value'}]
        result = self.resource.getNodes(resources=resources)
        self.assertIsInstance(result, list)
        self.assertIn('ussr', result)
                   
    def test_resource_getNodes_immediateValue_list(self):
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
        result = self.resource.getValue('vehicle:totalWeight', self.param)
        self.assertEqual(29390.0, result)

    def test_resource_getNodes_func_div(self):
        self.assertEqual(0.01701258931609391, self.resource.getValue('vehicle:powerWeightRatio', self.param))
        self.assertEqual(14.016600510789694, self.resource.getValue('vehicle:maxSpeed_medium', self.param))

    def test_resource_getNodes_func_mul(self):
        result = self.resource.getValue('vehicle:powerWeightRatioSI', self.param)
        self.assertEqual(12.51275944198707, result)

    def test_resource_getNodes_func_join(self):
        result = self.resource.getValue('vehicle:maxSpeed', self.param)
        self.assertEqual([16.565073330933274, 14.016600510789694, 7.922426375663741], result)

    def test_resource_getValue(self):
        self.assertEqual('T-34', self.resource.getValue('vehicle:shortUserString', self.param))
        resources = [{'file':'vehicles/{nation}/list.xml', 'xpath':'*/name()'}]
        result = self.resource.getValue(ctx=self.param, resources=resources, type='list')
        self.assertEqual(['Observer', 'R04_T-34', 'R02_SU-85', 'R01_IS', 'R03_BT-7'], result)


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
        self.assertEqual('T-34', self.resource.assignMap('#ussr_vehicles:T-34', 'gettext'))

    def test_resource_assingMap_split(self):
        self.assertEqual(['1.1', '1.3', '2.3'], self.resource.assignMap('1.1 1.3 2.3', 'split'))
            

class ConvertTestCase(unittest.TestCase):

    def test_convert_gettext(self):
        return
        self.assertEqual('T-34', vp.Convert.gettext('#ussr_vehicles:T-34'))
        
    def test_convert_map(self):
        return
        self.assertEqual('APCR', vp.Convert.map({'ARMOR_PIERCING':'AP', 'ARMOR_PIERCING_CR':'APCR'}, 'ARMOR_PIERCING_CR'))
        self.assertEqual('12', vp.Convert.map('[0]', '12 34'))


class VehicleDescriptorTestCase(unittest.TestCase):

    def setUp(self):
        return
        vdesc = vp.VehicleDescriptor(nation='ussr', vehicle='R04_T34')

    def test_property_get(self):
        return
        self.assertEqual('T-34', vdesc.get('vehicle:userString'))

if __name__ == '__main__':
    unittest.main()
    