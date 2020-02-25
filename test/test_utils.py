
import unittest

from lib.utils import VStatsFormatter


class VStatsFormatterTestCase(unittest.TestCase):

    def setUp(self):
        self.formatter = VStatsFormatter()

    def test_format_float(self):
        self.assertEqual('203.6', self.formatter.format('{:.1f}', 203.56))
        self.assertEqual('', self.formatter.format('{:.1f}', None))
        self.assertEqual('1,234,567', self.formatter.format('{:,.0f}', 1234567))

    def test_format_string(self):
        self.assertEqual('T-34 (R04_T-34), ', self.formatter.format('{} ({}), {}', 'T-34', 'R04_T-34', None))
        self.assertEqual(' (), ', self.formatter.format('{} ({}), {}', None, None, None))

    def test_format_exceptions(self):
        self.assertRaises(ValueError, self.formatter.format, '{:.1f}', '203.56')
