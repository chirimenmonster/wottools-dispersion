
import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from lib.config import g_config as config
from vehicleinfo import Command

class VehicleInfoTestCase(unittest.TestCase):

    def setUp(self):
        config.SCRIPTS_DIR = '../wot.scripts'
        config.GUI_DIR = 'test/data/res'
        config.schema = 'test/data/itemschema.json'
        config.suppress_unique = False
        config.suppress_empty = False
        config.sort = None
        config.csvoutput = None
        config.outputjson = True

    def test_listModule2(self):
        result = Command.listModule2('germany:8:lt', 'shell', 'shell:gravity')

