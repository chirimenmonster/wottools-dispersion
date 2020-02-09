
import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from lib.config import g_config as config
from lib.application import g_application as application
from lib.vehicleinfo2 import listVehicleModule

class VehicleInfoTestCase(unittest.TestCase):

    def setUp(self):
        config.GUI_DIR = 'test/data/res'
        config.scriptspkg = 'test/data/res/packages/scripts.pkg'
        config.schema = 'res/itemschema.json'
        config.outputjson = True
        application.setup(config)

    def test_listModule2(self):
        self.assertEqual([{'shell:gravity':'9.81'}], listVehicleModule('germany::lt,mt,ht,td', 'shell', 'shell:gravity'))
        result = listVehicleModule('::', 'shell', 'shell:gravity', sort='shell:gravity')
        self.assertEqual(26, len(result))
        self.assertEqual({'shell:gravity':'9.81'}, result[0])
        self.assertEqual({'shell:gravity':'190'}, result[-1])

    def test_listModule_secret(self):
        result = listVehicleModule('germany:10:td:secret', None, 'vehicle:index', sort='vehicle:id')
        expect = [{'vehicle:id': '66', 'vehicle:index': 'G98_Waffentrager_E100'},
            {'vehicle:id': '190', 'vehicle:index': 'G98_Waffentrager_E100_P'}]
        self.assertEqual(2, len(result))
        self.assertEqual(expect, result)
        result = listVehicleModule('germany::lt:secret', None, 'vehicle:index', sort='vehicle:id')
        self.assertEqual(7, len(result))
        result = listVehicleModule('germany:10:lt:secret', None, 'vehicle:index', sort='vehicle:id')
        self.assertEqual(0, len(result))
        self.assertEqual([], result)

