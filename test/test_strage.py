
import os
import sys
import unittest
import xml.etree.ElementTree as ET

from lib.strage import Strage


class StrageTestCase(unittest.TestCase):

    def test_strage_readStream(self):
        file = 'test/data/res/gui/gui_settings.xml'
        strage = Strage()
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
        strage = Strage()
        with open(file, 'rb') as fp:
            data = fp.read()
        self.assertFalse(strage.isCachedData(file))
        self.assertEqual(data, strage.readData(file))
        self.assertTrue(strage.isCachedData(file))
        self.assertEqual(data, strage.readData(file))


    def test_vpath_readXml(self):
        file = 'test/data/res/gui/gui_settings.xml'
        strage = Strage()
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
    

if __name__ == '__main__':
    unittest.main()
