
import unittest

from lib.config import Config
from lib.application import Application
from lib.query import queryVehicleModule

class VehicleInfoTestCase(unittest.TestCase):

    def setUp(self):
        config = Config()
        config.guipkg = 'test/data/res/packages/gui.pkg'
        config.scriptspkg = 'test/data/res/packages/scripts.pkg'
        config.schema = 'res/itemschema.json'
        self.app = Application()
        self.app.setup(config)

    def test_queryVehicleModule(self):
        result = queryVehicleModule(self.app, 'germany::lt,mt,ht,td', 'shell', 'shell:gravity')
        result = result.asPrimitive()
        self.assertEqual([{'shell:gravity':'9.81'}], result)
        result = queryVehicleModule(self.app, '::', 'shell', 'shell:gravity', sort='shell:gravity')
        result = result.asPrimitive()
        self.assertEqual(26, len(result))
        self.assertEqual({'shell:gravity':'9.81'}, result[0])
        self.assertEqual({'shell:gravity':'190'}, result[-1])

    def test_queryVehicleModule_secret(self):
        result = queryVehicleModule(self.app, 'germany:10:td:secret', None, 'vehicle:index', sort='vehicle:id')
        result = result.asPrimitive()
        expect = [{'vehicle:id': '66', 'vehicle:index': 'G98_Waffentrager_E100'},
            {'vehicle:id': '190', 'vehicle:index': 'G98_Waffentrager_E100_P'}]
        self.assertEqual(2, len(result))
        self.assertEqual(expect, result)
        result = queryVehicleModule(self.app, 'germany::lt:secret', None, 'vehicle:index', sort='vehicle:id')
        result = result.asPrimitive()
        self.assertEqual(7, len(result))
        result = queryVehicleModule(self.app, 'germany:10:lt:secret', None, 'vehicle:index', sort='vehicle:id')
        result = result.asPrimitive()
        self.assertEqual(0, len(result))
        self.assertEqual([], result)

    def test_queryVehicleModule_sort(self):
        result = queryVehicleModule(self.app, 'china:2:lt', 'gun', 'turret:index,gun:index', sort='turret:index,gun:index')
        result = result.asPrimitive()
        expect = [
            ['Turret_1_Ch07_Vickers_MkE_Type_BT26', '_47mm_QFSA'    ],
            ['Turret_2_Ch07_Vickers_MkE_Type_BT26', '_40mm_Pom_Pom' ],
            ['Turret_2_Ch07_Vickers_MkE_Type_BT26', '_45mm_20K'     ],
            ['Turret_2_Ch07_Vickers_MkE_Type_BT26', '_47mm_QFSA'    ]
        ]
        self.assertEqual(expect, [ [ v[k] for k in ('turret:index', 'gun:index') ] for v in result ])
        result = queryVehicleModule(self.app, 'china:2:lt', 'gun', 'gun:index', sort='turret:index,gun:index')
        result = result.asPrimitive()
        expect = [
            '_47mm_QFSA',
            '_40mm_Pom_Pom',
            '_45mm_20K'
        ]
        self.assertEqual(expect, [ v['gun:index'] for v in result ])
        result = queryVehicleModule(self.app, 'ussr:4:lt', None, 'vehicle:userString', sort='vehicle:userString')
        result = result.asPrimitive()
        expect = [
            'A-20',
            'T-80',
            'Valentine II'
        ]
        self.assertEqual(expect, [ v['vehicle:userString'] for v in result ])
        result = queryVehicleModule(self.app, 'ussr:4:lt', None, 'vehicle:userString', sort=',-vehicle:userString')
        result = result.asPrimitive()
        self.assertEqual(list(reversed(expect)), [ v['vehicle:userString'] for v in result ])
