
import unittest

from lib.application import g_application as app
from lib.config import g_config as config
from lib.resourcefactory import ResourceFactory, ResourceMeta, ResourceXml, ResourceImmediate, ResourceFunction


class ResourceFactoryTestCase(unittest.TestCase):

    def setUp(self):
        config.GUI_DIR = 'test/data/res'
        config.scriptspkg = 'test/data/res/packages/scripts.pkg'
        config.schema = 'res/itemschema.json'
        app.setup(config)

    def test_ResourceXml_1(self):
        desc = {
            "file":     "gui/gui_settings.xml",
            "xpath":    "settings/[name='nations_order']/value/item"
        }
        expect = ['germany', 'ussr', 'usa', 'japan', 'china', 'uk', 'france', 'czech', 'poland', 'italy', 'sweden']
        resource = ResourceFactory().create(desc)
        self.assertIsInstance(resource, ResourceMeta)
        self.assertIsInstance(resource, ResourceXml)
        self.assertEqual(expect, resource.getValue())

    def test_ResourceXml_2(self):
        desc = {
            "file":     "vehicles/{nation}/components/fuelTanks.xml",
            "xpath":    "ids/{fueltank}",
            "param":    { "fueltank": "vehicle:fueltank" }
        }
        ctx = { 'nation':'ussr', 'vehicle':'R04_T-34' }
        resource = ResourceFactory().create(desc)
        self.assertIsInstance(resource, ResourceXml)
        self.assertEqual(['203'], resource.getValue(ctx))

    def test_ResourceImmediate(self):
        desc = {
            "immediate": [ "LT", "MT", "HT", "TD", "SPG" ]
        }
        expect = ['LT', 'MT', 'HT', 'TD', 'SPG']
        resource = ResourceFactory().create(desc)
        self.assertIsInstance(resource, ResourceMeta)
        self.assertIsInstance(resource, ResourceImmediate)
        self.assertEqual(expect, resource.getValue())

    def test_ResourceFunction_sum(self):
        desc = {
            "func":     "sum()",
            "args":     [ "hull:health", "turret:health" ]
        }
        ctx = { 'hull:health':'320', 'turret:health':'130' }
        expect = 450
        resource = ResourceFactory().create(desc)
        self.assertIsInstance(resource, ResourceMeta)
        self.assertIsInstance(resource, ResourceFunction)
        self.assertEqual(expect, resource.getValue(ctx))

    def test_ResourceFunction_div(self):
        desc = {
            "func":     "div()",
            "args":     [ "engine:power", "vehicle:totalWeight" ]
        }
        ctx = { 'engine:power':'500', 'vehicle:totalWeight':'29390.0' }
        expect = 500 / 29390
        resource = ResourceFactory().create(desc)
        self.assertIsInstance(resource, ResourceMeta)
        self.assertIsInstance(resource, ResourceFunction)
        self.assertEqual(expect, resource.getValue(ctx))

    def test_ResourceFunction_mul(self):
        desc = {
            "func":     "mul()",
            "args":     [ "vehicle:powerWeightRatio", "physics:hpToWatts" ]
        }
        ctx = { 'vehicle:powerWeightRatio':'0.01701258931609391', 'physics:hpToWatts':'735.5' }
        expect = 0.01701258931609391 * 735.5
        resource = ResourceFactory().create(desc)
        self.assertIsInstance(resource, ResourceMeta)
        self.assertIsInstance(resource, ResourceFunction)
        self.assertEqual(expect, resource.getValue(ctx))

    def test_ResourceFunction_join(self):
        desc = {
            "func":     "join()",
            "args":     [ "vehicle:maxSpeed_hard", "vehicle:maxSpeed_medium", "vehicle:maxSpeed_soft" ]
        }
        ctx = { 'vehicle:maxSpeed_hard':'16.6', 'vehicle:maxSpeed_medium':'14.0', 'vehicle:maxSpeed_soft':'7.9' }
        expect = [ '16.6', '14.0', '7.9' ]
        resource = ResourceFactory().create(desc)
        self.assertIsInstance(resource, ResourceMeta)
        self.assertIsInstance(resource, ResourceFunction)
        self.assertEqual(expect, resource.getValue(ctx))

    def test_ResourceFunction_or(self):
        desc = {
            "func":     "or()",
            "args":     [ "vehicle:shortUserString", "vehicle:userString" ]
        }
        ctx = { 'vehicle:shortUserString':None, 'vehicle:userString':'T-34' }
        expect = 'T-34'
        resource = ResourceFactory().create(desc)
        self.assertIsInstance(resource, ResourceMeta)
        self.assertIsInstance(resource, ResourceFunction)
        self.assertEqual(expect, resource.getValue(ctx))
        ctx = { 'vehicle:shortUserString':'missing', 'vehicle:userString':'T-34' }
        expect = 'missing'
        resource = ResourceFactory().create(desc)
        self.assertIsInstance(resource, ResourceMeta)
        self.assertIsInstance(resource, ResourceFunction)
        self.assertEqual(expect, resource.getValue(ctx))

    def test_ResourceFunction_format(self):
        desc = {
            "func":     "format('{}: {}')",
            "args":      [ "shell:kindShort", "shell:userString" ]
        }
        ctx = { 'shell:kindShort':'AP', 'shell:userString':'UBR-354MA' }
        expect = 'AP: UBR-354MA'
        resource = ResourceFactory().create(desc)
        self.assertIsInstance(resource, ResourceMeta)
        self.assertIsInstance(resource, ResourceFunction)
        self.assertEqual(expect, resource.getValue(ctx))
