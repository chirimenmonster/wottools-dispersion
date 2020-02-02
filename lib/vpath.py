
import logging
import io
import re
import zipfile
from collections import namedtuple
import xml.etree.ElementTree as ET

from lib.XmlUnpacker import XmlUnpacker
from lib.translate import g_gettext

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

    def findall(self, key):
        return list(map(Element, self.__root.findall(key)))

    def findNodelist(self, key):
        return list(map(Element, self.__root.findall(key)))
    
    @property
    def tag(self):
        return self.__root.tag

    @property
    def text(self):
        return self.__root.text


class Resource(object):

    def __init__(self, strage, vpath, schema, param=None):
        self.__strage = strage
        self.__vpath = vpath
        self.__schema = schema
        self.__param = param
        self.__function = {
            'sum':  self.func_sum,
            'mul':  self.func_mul,
            'div':  self.func_div,
            'join': self.func_join,
            'or':   self.func_or,
        }

    def substitute(self, value, addparams=None):
        if addparams is not None:
            if self.__param is None:
                param = addparams
            else:
                param = self.__param.copy()
                param.update(addparams)
        else:
            if self.__param is None:
                param = None
            else:
                param = self.__param
        if param is not None:
            if isinstance(value, list):
                value = list(map(self.substitute, value))
            elif isinstance(value, str):
                value = value.format(**self.__param)
        return value

    def getFromFile(self, file, xpath, addparams=None):
        file = self.substitute(file)
        path = self.__vpath.getPathInfo(file)
        root = self.__strage.readXml(path)
        self.element = Element(root)
        xpath = self.substitute(xpath, addparams=addparams)
        xpath, n = re.subn(r'/name\(\)$', '', xpath)
        result = self.element.findall(xpath)
        if len(result) > 0:
            if n > 0:
                result = list(map(lambda x:x.tag, result))
            else:
                result = list(map(lambda x:x.text, result))
        return result

    def getNodes(self, tag=None, resources=None, order=None, addparams=None):
        if resources is None:
            resources = self.__schema[tag]['resources']
        for r in resources:
            if 'file' in r and 'xpath' in r:
                result = self.getFromFile(**r, addparams=addparams)
                if len(result) > 0:
                    break
            elif 'file' in r and 'custom' in r:
                raise NotImplementedError ('resource: {}'.format(r))           
            elif 'immediate' in r:
                result = self.substitute(r['immediate'], addparams=addparams)
                break
            elif 'func' in r:
                func = self.__function.get(r['func'], None)
                if func is None:
                    raise NotImplementedError ('func: {}'.format(r['func']))
                result = func(r['args'])
                break
            else:
                raise NotImplementedError('resource: {}'.format(r))
        if tag is not None and order is None:
            order = self.__schema[tag].get('order', None)
        if order is not None:
            result = self.sort(result, order)
        return result    

    def getRawValue(self, tag=None, resources=None, type=None, addparams=None):
        result = self.getNodes(tag, resources=resources, addparams=addparams)
        if isinstance(result, list):
            if type is None and tag is not None:
                valueType = self.__schema[tag].get('value', 'text')
            else:
                valueType = type
            if valueType == 'nodelist' or valueType == 'list':
                pass
            elif valueType == 'text':
                result = result[0]
                pass
            elif valueType == 'float':
                result = result[0]
                pass
            else:
                raise NotImplementedError('value: {}'.format(valueType))
        return result

    def getValue(self, tag):
        pos = None
        match = re.fullmatch(r'^(.*)\[(\d*)\]$', tag)
        if match:
            tag = match.group(1)
            pos = int(match.group(2))
        if 'addparams' in self.__schema[tag]:
            addparams = {}
            for p in self.__schema[tag]['addparams']:
                xtag = p['xtag']
                value = self.getValue(p['value'])
                addparams = {xtag:value}
        else:
            addparams = None
        result = self.getRawValue(tag, addparams=addparams)
        result = self.assignMap(tag, result)
        if pos is not None:
            result = result[pos]
        return result

    def assignMap(self, tag, value):
        rule = self.__schema[tag].get('map', None)
        if rule is None:
            result = value
        elif isinstance(rule, dict):
            result = ' '.join(filter(None, map(lambda x: rule.get(x, None), value.split())))
        elif rule == 'roman':
            raise NotImplementedError
        elif rule == 'gettext':
            result = g_gettext.translate(value)
        elif rule == 'split':
            result = value.split()
        elif rule == '[0]':
            raise NotImplementedError
        return result

    def sort(self, values, order):
        if not isinstance(values, list):
            return values
        values = sorted(values, key=lambda x:order.index(x) if x in order else float('inf'))
        return values

    def func_sum(self, args):
        values = list(map(lambda x:float(self.getValue(x)), args))
        return sum(values)

    def func_div(self, args):
        try:
            values = list(map(lambda x:float(self.getValue(x)), args))
        except:
            values = list(map(lambda x:self.getValue(x), args))
            print(values)
            raise
        result = values.pop(0)
        for v in values:
            result /= v
        return result

    def func_mul(self, args):
        values = list(map(lambda x:float(self.getValue(x)), args))
        result = 1.0
        for v in values:
            result *= v
        return result

    def func_join(self, args):
        values = list(map(lambda x:self.getValue(x), args))
        result = []
        for v in values:
            if isinstance(v, list):
                result.extend(v)
            else:
                result.append(v)
        return result

    def func_or(self, args):
        values = list(map(lambda x:self.getValue(x), args))
        result = None
        for v in values:
            result = result or v
        return result
