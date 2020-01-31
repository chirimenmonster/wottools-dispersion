
import logging
import io
import re
import zipfile
from collections import namedtuple
import xml.etree.ElementTree as ET

from lib.XmlUnpacker import XmlUnpacker

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


class Strage(object):

    def __init__(self):
        self.__cachedData = {}
        self.__cachedXml = {}

    def readStream(self, path, pkg=None):
        if not isinstance(path, PathInfo):
            path, file = PathInfo(path, pkg), path
        else:
            file, pkg = path
        if pkg:
            try:
                with zipfile.ZipFile(pkg, 'r') as zip:
                    with zip.open(file, 'r') as fp:
                        stream = io.BytesIO(fp.read())
            except FileNotFoundError:
                raise FileNotFoundError('pkgfile not found: {}'.format(pkg))
            except KeyError:
                raise KeyError('file not found: {}, in pkgfile: {}'.format(file, pkg))
        else:
            try:
                with open(file, 'rb') as fp:
                    stream = io.BytesIO(fp.read())
            except FileNotFoundError:
                raise FileNotFoundError('cannot open file: {}'.format(file))
        return stream

    def readData(self, path, pkg=None):
        if not isinstance(path, PathInfo):
            path, file = PathInfo(path, pkg), path
        if path in self.__cachedData:
            return self.__cachedData[path]
        data = self.readStream(path).read()
        self.__cachedData[path] = data
        return data

    def readXml(self, path, pkg=None):
        if not isinstance(path, PathInfo):
            path, file = PathInfo(path, pkg), path
        if path in self.__cachedXml:
            return self.__cachedXml[path]
        xmlunpacker = XmlUnpacker()
        stream = self.readStream(path)
        try:
            root = xmlunpacker.read(stream)
        except ET.ParseError:
            stream.seek(0)
            data = stream.read()
            data = re.sub(r'<xmlns:xmlref>.*?</xmlns:xmlref>', r'', data.decode('utf-8')).encode('utf-8')
            try:
                root = xmlunpacker.read(io.BytesIO(data))
            except:
                logger.error('cannot parse file: {}'.format(path))
                raise
        self.__cachedXml[path] = root
        return root

    def isCachedData(self, path, pkg=None):
        if not isinstance(path, PathInfo):
            path = PathInfo(path, pkg)
        return path in self.__cachedData

    def isCachedXml(self, path, pkg=None):
        if not isinstance(path, PathInfo):
            path = PathInfo(path, pkg)
        return path in self.__cachedXml


class Element(object):

    def __init__(self, root):
        self.__root = root

    def findText(self, key):
        return self.__root.findtext(key)
        
    def findNodename(self, key):
        node = self.__root.find(key)
        return node.tag if node else None

    def findNodelist(self, key):
        return list(map(Element, self.__root.findall(key)))
    
    @property
    def tag(self):
        return self.__root.tag

    @property
    def text(self):
        return self.__root.text
