
import os
import sys
import unittest

from lib.application import Settings

class SettingssTestCase(unittest.TestCase):

    def setUp(self):
        self.itemschema = 'res/itemschema.json'
        self.guisettings_items = 'res/guisettings_items.json'
        self.guisettings_selectors = 'res/guisettings_selectors.json'
        self.guisettings_titles = 'res/guisettings_titles.json'
        
    def test_settings_itemschema(self):
        settings = Settings()
        settings.add('schema', self.itemschema)
        result = settings.schema
        self.assertIsInstance(result, dict)
        self.assertIn('settings:nationsOrder', result)

    def test_settings_guisettings(self):
        settings = Settings()
        settings.add('guiitems', self.guisettings_items)
        settings.add('guiselectors', self.guisettings_selectors)
        settings.add('guititles', self.guisettings_titles)
        self.assertIsInstance(settings.guiitems, dict)
        self.assertIn('columns', settings.guiitems)
        self.assertIsInstance(settings.guiselectors, list)
        self.assertIsInstance(settings.guiselectors[0], list)
        self.assertIn('id', settings.guiselectors[0][0])
        self.assertIsInstance(settings.guititles, list)
        self.assertIn('label', settings.guititles[0])
