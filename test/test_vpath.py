
import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from lib import vpath as vp


class VPathTestCase(unittest.TestCase):
    def test_vpath(self):
        vpath = vp.VPath(basedir='c:/Games/World_of_Tanks_ASIA', pkgpath='res/packages')
        self.assertEqual({
            'pkg':      'c:/Games/World_of_Tanks_ASIA/res/packages/scripts.pkg',
            'rpath':    'scripts/item_defs/vehicles/ussr/list.xml'
        }, vpath.pkgpath('vehicles/ussr/list.xml'))
        self.assertEqual({
            'pkg':      'c:/Games/World_of_Tanks_ASIA/res/packages/gui.pkg',
            'rpath':    'gui/gui_settings.xml'
        }, vpath.pkgpath('gui/gui_settings.xml'))

    def test_vpath_scriptsdir(self):
        vpath = vp.VPath(basedir='c:/Games/World_of_Tanks_ASIA', pkgpath='res/packages', scriptsdir='d:/git/wot.scripts')
        self.assertEqual({
            'path':     'd:/git/wot.scripts/scripts/item_defs/vehicles/ussr/list.xml'
        }, vpath.pkgpath('vehicles/ussr/list.xml'))
        self.assertEqual({
            'pkg':      'c:/Games/World_of_Tanks_ASIA/res/packages/gui.pkg',
            'rpath':    'gui/gui_settings.xml'
        }, vpath.pkgpath('gui/gui_settings.xml'))

    def test_vpath_guidir(self):
        vpath = vp.VPath(basedir='c:/Games/World_of_Tanks_ASIA', pkgpath='res/packages', guidir='./test')
        self.assertEqual({
            'pkg':      'c:/Games/World_of_Tanks_ASIA/res/packages/scripts.pkg',
            'rpath':    'scripts/item_defs/vehicles/ussr/list.xml'
        }, vpath.pkgpath('vehicles/ussr/list.xml'))
        self.assertEqual({
            'path':     './test/gui/gui_settings.xml'
        }, vpath.pkgpath('gui/gui_settings.xml'))

if __name__ == '__main__':
    unittest.main()
    