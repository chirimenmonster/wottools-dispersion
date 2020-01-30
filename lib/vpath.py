
import re

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

class _RePattern(object):
    def __init__(self, pattern=None, path=None, pkg=None):
        self.pattern = pattern
        self.path = path
        self.pkg = pkg
        self.dir = None

class VPath(object):

    def __init__(self, basedir=None, pkgpath=None, scriptsdir=None, guidir=None):
        self.__basedir = basedir
        self.__pkgpath = pkgpath
        self.__pattern = []
        for k,v in _config.items():
            p = _RePattern(**v)
            if scriptsdir and p.pkg == 'scripts.pkg':
                p.pkg = None
                p.dir = scriptsdir
            elif guidir and p.pkg == 'gui.pkg':
                p.pkg = None
                p.dir = guidir
            self.__pattern.append(p)

    def pkgpath(self, target):
        rpath = target
        for p in self.__pattern:
            (rpath, n) = re.subn(p.pattern, p.path, rpath)
            if n == 1:
                pkg = p.pkg
                break
        assert n == 1, rpath
        if p.dir:
            filepath = '/'.join([ p.dir, rpath ])
            result = { 'path':filepath }
        else:
            pkgpath = '/'.join([ self.__basedir, self.__pkgpath, pkg ])
            result = { 'pkg':pkgpath, 'rpath':rpath }
        return result
        

def readData(domain, target=None):
    vpath = config.DATA[domain]['vpath'] + ('/' + target if target else '')

    if config.DATA[domain]['extracted']:
        path = '/'.join([ config.DATA[domain]['extracted'], vpath.split('/', 1)[1] ])
        try:
            with open(path, 'rb') as file:
                stream = io.BytesIO(file.read())
        except:
            logger.debug('cannot open file: {}'.format(path))
            raise
    else:
        pkgpath = '/'.join([ config.BASE_DIR, config.PKG_RELPATH, config.DATA[domain]['packed'] ])
        try:
            with zipfile.ZipFile(pkgpath, 'r') as zip:
                with zip.open(vpath, 'r') as data:
                    stream = io.BytesIO(data.read())
        except:
            logger.debug('cannot open vfile: {}, {}'.format(pkgpath, vpath))
            raise
    return stream
