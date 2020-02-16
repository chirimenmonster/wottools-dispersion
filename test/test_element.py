import os
import sys
import unittest
from operator import attrgetter

from lib.element import Element


class ElementTestCase(unittest.TestCase):

    def test_element_float(self):
        schema = {
            'value':    'float',
            'format':   '.1f',
        }
        obj = Element('1.324', schema)
        self.assertEqual('1.324', obj.str)
        self.assertEqual(1.324, obj.value)
        self.assertEqual(5, obj.strlen)
        self.assertEqual('1.3', obj.getFormattedString())
        self.assertEqual('     1.3', obj.getFormattedString(width=8))

    def test_element_str(self):
        schema = {
        }
        obj = Element('foobar', schema)
        self.assertEqual('foobar', obj.str)
        self.assertEqual('foobar', obj.value)
        self.assertEqual(6, obj.strlen)
        self.assertEqual('foobar', obj.getFormattedString())
        self.assertEqual('foobar  ', obj.getFormattedString(width=8))

    def test_element_sort_float(self):
        schema = {
            'value':    'float',
            'format':   '.1f',
        }
        objs = [
            Element('10.3', schema),
            Element('8.324', schema),
        ]
        result = sorted(objs, key=attrgetter('order'))
        self.assertEqual(['8.324', '10.3'], list(map(lambda x:x.str, result)))

    def test_element_sort_str(self):
        schema = {
        }
        objs = [
            Element('10.3', schema),
            Element('8.324', schema),
        ]
        result = sorted(objs, key=attrgetter('order'))
        self.assertEqual(['10.3', '8.324'], list(map(lambda x:x.str, result)))
