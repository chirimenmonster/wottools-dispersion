
import unittest

from lib.itemtype import TypeFactory


class TypeFactoryTestCase(unittest.TestCase):

    def setUp(self):
        self.factory = TypeFactory(None)

    def test_TypeDefault(self):
        itemtype = self.factory.create(None)
        self.assertEqual('test', itemtype.getValue('test'))
        self.assertEqual('test', itemtype.getValue(['test']))
        self.assertEqual('test test2', itemtype.getValue(['test', 'test2']))
        self.assertEqual(5, itemtype.getValue(5))
        self.assertEqual(5, itemtype.getValue([5]))
        self.assertEqual('5 7', itemtype.getValue([5, 7]))
        self.assertEqual({'test':'value'}, itemtype.getValue({'test':'value'}))
        self.assertEqual(None, itemtype.getValue(None))
        self.assertEqual(None, itemtype.getValue([]))
        self.assertEqual(None, itemtype.getValue({}))

    def test_TypeOrig(self):
        itemtype = self.factory.create('list')
        self.assertEqual(['test', 'test2'], itemtype.getValue(['test', 'test2']))
        itemtype = self.factory.create('dict')
        self.assertEqual(['test', 'test2'], itemtype.getValue(['test', 'test2']))
        self.assertEqual({'test':5, 'test2':7}, itemtype.getValue({'test':5, 'test2':7}))

    def test_TypeText(self):
        itemtype = self.factory.create('text')
        self.assertEqual('test', itemtype.getValue('test'))
        self.assertEqual('test', itemtype.getValue(['test']))
        self.assertEqual('test test2', itemtype.getValue(['test', 'test2']))
        self.assertEqual(5, itemtype.getValue(5))
        self.assertEqual('5', itemtype.getValue([5]))
        self.assertEqual('5 7', itemtype.getValue([5, 7]))
        self.assertEqual({'test':'value'}, itemtype.getValue({'test':'value'}))
        self.assertEqual(None, itemtype.getValue(None))
        self.assertEqual(None, itemtype.getValue([]))
        self.assertEqual(None, itemtype.getValue({}))

    def test_TypeInt(self):
        itemtype = self.factory.create('int')
        self.assertEqual('5', itemtype.getValue('5'))
        self.assertEqual(5.2, itemtype.getValue(5.2))
        self.assertEqual(5.2, itemtype.getValue([5.2]))
        with self.assertRaises(ValueError):
            _ = self.assertEqual('5.2', itemtype.getValue('5.2'))
        with self.assertRaises(ValueError):
            _ = itemtype.getValue([5.2, 7.3])
        with self.assertRaises(ValueError):
            _ = itemtype.getValue('test')
        self.assertEqual(None, itemtype.getValue(None))
        self.assertEqual(None, itemtype.getValue([]))
        self.assertEqual(None, itemtype.getValue({}))

    def test_TypeFloat(self):
        itemtype = self.factory.create('float')
        self.assertEqual('5.2', itemtype.getValue('5.2'))
        self.assertEqual(5.2, itemtype.getValue(5.2))
        self.assertEqual(5.2, itemtype.getValue([5.2]))
        with self.assertRaises(ValueError):
            _ = itemtype.getValue([5.2, 7.3])
        with self.assertRaises(ValueError):
            _ = itemtype.getValue('test')
        self.assertEqual(None, itemtype.getValue(None))
        self.assertEqual(None, itemtype.getValue([]))
        self.assertEqual(None, itemtype.getValue({}))
