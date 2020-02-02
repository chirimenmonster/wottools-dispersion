
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
        strage = vp.Strage()
        vpath = vp.VPath(scriptsdir='test/data/res')
        with open('res/itemschema.json', 'r') as fp:
            schema = json.load(fp)
        param = {'nation':'ussr', 'vehicle':'R04_T-34'}
        self.resource = vp.Resource(strage, vpath, schema, param)
    
    def test_resource_getResources(self):
        resources = [{'file':'vehicles/{nation}/list.xml', 'xpath':'{vehicle}/shortUserString'},
            {'file':'vehicles/{nation}/list.xml','xpath':'{vehicle}/userString'}]
        self.assertEqual(resources, self.resource.getResources('vehicle:shortUserString'))
    
    def test_resource_getFromFile(self):
        result = self.resource.getFromFile('vehicles/{nation}/list.xml', '{vehicle}/userString')
        self.assertEqual('#ussr_vehicles:T-34', result[0].text)
        result = self.resource.getFromFile('vehicles/{nation}/list.xml', '{vehicle}/missing')
        self.assertEqual(0, len(result))
        with self.assertRaises(FileNotFoundError):
            result = self.resource.getFromFile('vehicles/{nation}/missing', '{vehicle}/userString')
    
    def test_resource_getNodes(self):
        nodes = self.resource.getFromFile('vehicles/{nation}/list.xml', '{vehicle}/userString')
        self.assertEqual(1, len(nodes))
        self.assertEqual('#ussr_vehicles:T-34', nodes[0].text)

    def test_resource_getRawValue(self):
        self.assertEqual('#ussr_vehicles:T-34', self.resource.getRawValue('vehicle:shortUserString'))

    def test_resource_assingMap(self):
        value = self.resource.getRawValue('vehicle:type')
        self.assertIn('mediumTank', value.split())
        self.assertEqual('MT', self.resource.assignMap('vehicle:type', value))
        self.assertEqual('MT HT', self.resource.assignMap('vehicle:type', ' unknown mediumTank unknown heavyTank secret '))

    def test_resource_assingMap_gettext(self):
        value = self.resource.getRawValue('vehicle:userString')
        self.assertEqual('#ussr_vehicles:T-34', value)
        self.assertEqual('T-34', self.resource.assignMap('vehicle:userString', value))

    def test_resource_assignFunc(self):
        pass
            

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
    