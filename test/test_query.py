
import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from lib.config import g_config as config
from lib.application import g_application as application
from lib.query import queryVehicleModule

class VehicleInfoTestCase(unittest.TestCase):

    def setUp(self):
        config.GUI_DIR = 'test/data/res'
        config.scriptspkg = 'test/data/res/packages/scripts.pkg'
        config.schema = 'res/itemschema.json'
        config.outputjson = True
        application.setup(config)

    def test_queryVehicleModule(self):
        result = queryVehicleModule('germany::lt,mt,ht,td', 'shell', 'shell:gravity')
        result = result.asPrimitive()
        self.assertEqual([{'shell:gravity':'9.81'}], result)
        result = queryVehicleModule('::', 'shell', 'shell:gravity', sort='shell:gravity')
        result = result.asPrimitive()
        self.assertEqual(26, len(result))
        self.assertEqual({'shell:gravity':'9.81'}, result[0])
        self.assertEqual({'shell:gravity':'190'}, result[-1])

    def test_queryVehicleModule_secret(self):
        result = queryVehicleModule('germany:10:td:secret', None, 'vehicle:index', sort='vehicle:id')
        result = result.asPrimitive()
        expect = [{'vehicle:id': '66', 'vehicle:index': 'G98_Waffentrager_E100'},
            {'vehicle:id': '190', 'vehicle:index': 'G98_Waffentrager_E100_P'}]
        self.assertEqual(2, len(result))
        self.assertEqual(expect, result)
        result = queryVehicleModule('germany::lt:secret', None, 'vehicle:index', sort='vehicle:id')
        result = result.asPrimitive()
        self.assertEqual(7, len(result))
        result = queryVehicleModule('germany:10:lt:secret', None, 'vehicle:index', sort='vehicle:id')
        result = result.asPrimitive()
        self.assertEqual(0, len(result))
        self.assertEqual([], result)

    def test_queryVehicleModule_sort(self):
        result = queryVehicleModule('china:2:lt', 'gun', 'turret:index,gun:index', sort='turret:index,gun:index')
        result = result.asPrimitive()
        expect = [
            ['Turret_1_Ch07_Vickers_MkE_Type_BT26', '_47mm_QFSA'    ],
            ['Turret_2_Ch07_Vickers_MkE_Type_BT26', '_40mm_Pom_Pom' ],
            ['Turret_2_Ch07_Vickers_MkE_Type_BT26', '_45mm_20K'     ],
            ['Turret_2_Ch07_Vickers_MkE_Type_BT26', '_47mm_QFSA'    ]
        ]
        self.assertEqual(expect, [ [ v[k] for k in ('turret:index', 'gun:index') ] for v in result ])
        result = queryVehicleModule('china:2:lt', 'gun', 'gun:index', sort='turret:index,gun:index')
        result = result.asPrimitive()
        expect = [
            '_47mm_QFSA',
            '_40mm_Pom_Pom',
            '_45mm_20K'
        ]
        self.assertEqual(expect, [ v['gun:index'] for v in result ])
        result = queryVehicleModule('ussr:4:lt', None, 'vehicle:userString', sort='vehicle:userString')
        result = result.asPrimitive()
        expect = [
            'A-20',
            'T-80',
            'Valentine II'
        ]
        self.assertEqual(expect, [ v['vehicle:userString'] for v in result ])
        result = queryVehicleModule('ussr:4:lt', None, 'vehicle:userString', sort=',-vehicle:userString')
        result = result.asPrimitive()
        self.assertEqual(list(reversed(expect)), [ v['vehicle:userString'] for v in result ])
