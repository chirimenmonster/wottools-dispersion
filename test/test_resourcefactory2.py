
import unittest

from lib.application import g_application as app
from lib.config import g_config as config
from lib.resourcefactory import ResourceFactory


class ResourceFactoryTestCase2(unittest.TestCase):

    def setUp(self):
        config.GUI_DIR = None
        config.scriptspkg = None
        config.schema = 'res/itemschema.json'
        app.setup(config)

    def test_ResourceXml_1(self):
        desc = {
            "file":     "gui/gui_settings.xml",
            "xpath":    "setting/[name='nations_order']/value/item"
        }
        expect = ['germany', 'ussr', 'usa', 'japan', 'china', 'uk', 'france', 'czech', 'poland', 'italy', 'sweden']
        resource = ResourceFactory(app).create(desc)
        self.assertEqual(expect, resource.getValue())
