
import re
from collections import namedtuple
import logging
import traceback

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

_config = {
    'vehicles': {
        'pattern':  r'^vehicles',
        'path':     'scripts/item_defs/vehicles',
        'pkg':      'scripts.pkg'
    },
    'gui':  {
        'pattern':  r'^gui',
        'path':     'gui',
        'pkg':      'gui.pkg'
    }
}

PathInfo = namedtuple('PathInfo', 'path pkg', defaults=(None,))


class VPath(object):

    RePattern = namedtuple('RePattern', 'pattern path pkg pkgdir dir', defaults=(None, None))

    def __init__(self, pkgdir=None, scriptsdir=None, guidir=None, scriptspkg=None, guipkg=None):
        self.__pattern = []
        self.__cachedData = {}
        self.__cachedXml = {}
        for k,v in _config.items():
            p = self.RePattern(**v)
            if pkgdir:
                p = p._replace(pkgdir=pkgdir)
            if p.pkg == 'scripts.pkg':
                if scriptsdir:
                    p = p._replace(pkg=None, dir=scriptsdir)
                elif scriptspkg:
                    p = p._replace(pkgdir=None, pkg=scriptspkg)
            elif p.pkg == 'gui.pkg':
                if guidir:
                    p = p._replace(pkg=None, dir=guidir)
                elif guipkg:
                    p = p._replace(pkgdir=None, pkg=guipkg)
            self.__pattern.append(p)

    def getPathInfo(self, target):
        rpath = target
        for p in self.__pattern:
            (rpath, n) = re.subn(p.pattern, p.path, rpath)
            if n == 1:
                pkg = p.pkg
                break
        assert n == 1, rpath
        if p.dir:
            filepath = '/'.join([ p.dir, rpath ])
            result = PathInfo(filepath)
        else:
            pkgpath = '/'.join([ p.pkgdir, pkg ]) if p.pkgdir else pkg
            result = PathInfo(rpath, pkgpath)
        return result
