
import unittest

from lib.config import Config
from lib.application import Application


class ResourceTestCase(unittest.TestCase):

    def setUp(self):
        config = Config()
        config.guipkg = 'test/data/res/packages/gui.pkg'
        config.scriptspkg = 'test/data/res/packages/scripts.pkg'
        config.schema = 'res/itemschema.json'
        config.localedir = 'test/data/res'
        app = Application()
        app.setup(config)
        self.resource = app.resource
        self.ctx = {'nation':'ussr', 'vehicle':'R04_T-34', 'vehicle_siege':'R04_T-34',
            'chassis':'T-34_mod_1943', 'turret':'T-34_mod_1942',
            'engine':'V-2-34', 'radio':'_9RM', 'gun':'_76mm_S-54'}
        
    def test_resource_getNodes_immediateValue_string(self):
        self.assertEqual('ussr', self.resource.getValue('vehicle:nation', self.ctx))
        self.assertEqual(735.5, self.resource.getValue('physics:hpToWatts', self.ctx))

    def test_resource_getNodes_func_sum(self):
        weight = {'hull:weight': 15000, 'chassis:weight':8000, 'turret:weight':3900, 'engine:weight':750,
            'fueltank:weight':250, 'radio:weight':100, 'gun:weight':1390 }
        for m,w in weight.items():
            result = self.resource.getValue(m, self.ctx)
            self.assertEqual(str(w), result)
        result = self.resource.getValue('vehicle:totalWeight', self.ctx)
        self.assertEqual(29390.0, result)

    def test_resource_getNodes_func_div(self):
        result = self.resource.getValue('engine:power', self.ctx)
        result = self.resource.getValue('vehicle:totalWeight', self.ctx)
        self.assertEqual(0.01701258931609391, self.resource.getValue('vehicle:powerWeightRatio', self.ctx))
        self.assertEqual(14.016600510789694, self.resource.getValue('vehicle:maxSpeed_medium', self.ctx))

    def test_resource_getNodes_func_mul(self):
        result = self.resource.getValue('vehicle:powerWeightRatioSI', self.ctx)
        self.assertEqual(12.51275944198707, result)

    def test_resource_getNodes_func_join(self):
        result = self.resource.getValue('vehicle:maxSpeed', self.ctx)
        self.assertEqual([16.565073330933274, 14.016600510789694, 7.922426375663741], result)

    def test_resource_getValue_1(self):
        return
        self.assertEqual('T-34', self.resource.getValue('vehicle:shortUserString', self.ctx))

    def test_resource_getValue_2(self):
        return
        resources = [{'file':'vehicles/{nation}/list.xml', 'xpath':'name(*)'}]
        result = self.resource.getValue(ctx=self.ctx, resources=resources, type='list')
        self.assertEqual(['Observer', 'R04_T-34', 'R02_SU-85', 'R01_IS', 'R03_BT-7'], result)

    def test_resource_getValue_3(self):
        resources = [{'file':'vehicles/{nation}/list.xml', 'xpath':'position(R04_T-34)'}]
        result = self.resource.getValue(ctx=self.ctx, resources=resources, type='int')
        self.assertEqual(2, result)

    def test_resource_getValue_4(self):
        result = self.resource.getValue('settings:tiersLabel')
        expect = {'1':'I', '2':'II', '3':'III', '4':'IV', '5': 'V',
                    '6':'VI', '7':'VII', '8':'VIII', '9':'IX', '10':'X' }
        self.assertEqual(expect, result)

    def test_resource_secret(self):
        result = self.resource.getValue('vehicle:secret', self.ctx)
        print('result={}'.format(repr(result)))
    

if __name__ == '__main__':
    unittest.main()
    