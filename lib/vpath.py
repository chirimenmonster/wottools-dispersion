
import logging
import os
import io
import re
import json
import zipfile
from collections import namedtuple
import xml.etree.ElementTree as ET

import traceback

from lib.resources import TIERS_LABEL
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


class Settings(object):

    def __init__(self, dir=None, schema=None):
        self.__dir = dir
        if schema:
            self.__path_schema = schema
        else:
            self.__path_schema = os.path.join(self.__dir, 'itemschema.json')
        self.__schema = None

    @property
    def schema(self):
        if self.__schema is None:
            with open(self.__path_schema, 'r') as fp:
                self.__schema = json.load(fp)
        return self.__schema


class Strage(object):

    def __init__(self):
        self.__cachedData = {}
        self.__cachedXml = {}
        self.__cachedZip = {}

    def readStream(self, path, pkg=None):
        if not isinstance(path, PathInfo):
            path, file = PathInfo(path, pkg), path
        else:
            file, pkg = path
        if pkg:
            try:
                if pkg in self.__cachedZip:
                    zip = self.__cachedZip[pkg]
                else:
                    zip = zipfile.ZipFile(pkg, 'r')
                    self.__cachedZip[pkg] = zip
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
        self.__gettext = None
        self.__param = param
        self.__function = {
            'sum':  self.func_sum,
            'mul':  self.func_mul,
            'div':  self.func_div,
            'join': self.func_join,
            'or':   self.func_or,
            'format':   self.func_format,
        }

    @property
    def gettext(self):
        return self.__gettext
        
    @gettext.setter
    def gettext(self, obj):
        self.__gettext = obj

    def getFromFile(self, file, xpath, param=None, ctx=None):
        if ctx is None:
            ctx = {}
        if param is not None:
            newctx = ctx.copy()
            for xtag, value in param.items():
                newctx[xtag] = self.getRefValue(value, ctx)
            ctx = newctx
        file = self.substitute(file, ctx)
        xpath = self.substitute(xpath, ctx)
        path = self.__vpath.getPathInfo(file)
        root = self.__strage.readXml(path)
        self.element = Element(root)
        xpath, n = re.subn(r'/name\(\)$', '', xpath)
        try:
            result = self.element.findall(xpath)
            result = list(filter(lambda x:x.tag != 'xmlns:xmlref', result))
        except:
            raise ValueError('xpath={}'.format(xpath))
        if len(result) > 0:
            if n == 1:
                result = list(map(lambda x:x.tag, result))
            else:
                result = list(map(lambda x:x.text, result))
        return result

    def getNodes(self, resources=None, ctx=None):
        for r in resources:
            if 'file' in r and 'xpath' in r:
                file = r['file']
                xpath = r['xpath']
                param = r.get('param', None)
                try:
                    result = self.getFromFile(file, xpath, param, ctx)
                except FileNotFoundError:
                    if r == resources[-1]:
                        raise
                    continue
                if len(result) > 0:
                    break
            elif 'immediate' in r:
                result = self.substitute(r['immediate'], ctx)
                break
            elif 'func' in r:
                match = re.fullmatch(r'(.*)\((.*)\)', r['func'])
                if match is None or match.group(1) is None:
                    raise NotImplementedError ('func: {}'.format(r['func']))
                func = self.__function.get(match.group(1), None)
                arg0 = match.group(2)
                if func is None:
                    raise NotImplementedError ('func: {}'.format(r['func']))
                result = func(arg0, r['args'], ctx=ctx)
                break
            else:
                raise NotImplementedError('resource: {}'.format(r))
        return result

    def getValue(self, tag=None, ctx=None, resources=None, order=None, type=None, map=None):
        if tag is not None:
            schema = self.__schema[tag]
            if resources is None:
                resources = schema.get('resources', None)
            if order is None:
                order = schema.get('order', None)
            if type is None:
                type = schema.get('value', None)
            if map is None:
                map = schema.get('map', None)
        try:
            result = self.getNodes(resources=resources, ctx=ctx)
        except KeyError as e:
            raise KeyError(e, resources, ctx) from e
            #raise
        result = self.sort(result, order)
        result = self.convert(result, type)
        result = self.assignMap(result, map)
        return result

    def getRefValue(self, tag, ctx=None):
        pos = None
        match = re.fullmatch(r'^(.*)\[(\d*)\]$', tag)
        if match:
            tag = match.group(1)
            pos = int(match.group(2))
        result = self.getValue(tag, ctx)
        if pos is not None:
            result = result[pos]
        return result

    def mergeparams(self, ctx, addparams=None):
        if ctx is not None and addparams is not None:
            ctx = ctx.copy()
            ctx.update(addparams)
        elif ctx is None:
            ctx = addparams
        return ctx

    def substitute(self, value, ctx):
        if ctx is None:
            return value
        if isinstance(value, list):
            value = list(map(lambda x,c=ctx:self.substitute(x, c), value))
        elif isinstance(value, str):
            try:
                value = value.format(**ctx)
            except KeyError as e:
                raise KeyError(e, value, ctx) from e
            except TypeError as e:
                raise TypeError(e.args[0], value, ctx) from e
        return value

    def convert(self, value, datatype=None):
        if not isinstance(value, list):
            return value
        if datatype is None:
            if len(value) == 0:
                value = None
            elif len(value) == 1:
                value = value[0]
            else:
                value = ' '.join(map(str, value))
        elif datatype == 'text':
            value = ' '.join(str(value))
        elif datatype == 'float':
            if len(value) != 1:
                raise ValueError('data type "float" must one value: {}'.format(value))
            value = value[0]
        elif datatype == 'list':
            pass
        else:
            raise NotImplementedError('value: {}'.format(datatype))
        return value

    def assignMap(self, value, rule):
        if rule is None:
            return value
        if isinstance(rule, dict):
            result = ' '.join(filter(None, map(lambda x: rule.get(x, None), value.split())))
        elif rule == 'roman()':
            result = TIERS_LABEL.get(value, None)
        elif rule == 'gettext()':
            if self.gettext is None:
                raise AttributeError('translate engine is not prepared.')
            result = self.gettext.translate(value)
        elif rule.startswith('split()'):
            match = re.fullmatch(r'split\(\)(\[(\d+)\])?', rule)
            if match is None:
                raise NotImplementedError('map rule: {}'.format(rule))
            result = value.split()
            if match.group(2) is not None:
                pos = int(match.group(2))
                result = result[pos]
        else:
            raise NotImplementedError('map rule: {}'.format(rule))
        return result

    def sort(self, values, order):
        if order is None:
            return values
        if not isinstance(values, list):
            return values
        values = sorted(values, key=lambda x:order.index(x) if x in order else float('inf'))
        return values

    def func_sum(self, arg0, args, ctx=None):
        values = list(map(lambda x,c=ctx:float(self.getRefValue(x, c)), args))
        return sum(values)

    def func_div(self, arg0, args, ctx=None):
        try:
            values = list(map(lambda x,c=ctx:float(self.getRefValue(x, c)), args))
        except:
            values = list(map(lambda x,c=ctx:self.getRefValue(x, c), args))
            raise
        result = values.pop(0)
        for v in values:
            result /= v
        return result

    def func_mul(self, arg0, args, ctx=None):
        values = list(map(lambda x,c=ctx:float(self.getRefValue(x, c)), args))
        result = 1.0
        for v in values:
            result *= v
        return result

    def func_join(self, arg0, args, ctx=None):
        values = list(map(lambda x,c=ctx:self.getRefValue(x, c), args))
        result = []
        for v in values:
            if isinstance(v, list):
                result.extend(v)
            else:
                result.append(v)
        return result

    def func_or(self, arg0, args, ctx=None):
        values = list(map(lambda x,c=ctx:self.getRefValue(x, c), args))
        result = None
        for v in values:
            result = result or v
        return result

    def func_format(self, arg0, args, ctx=None):
        match = re.fullmatch(r'\'(.*)\'', arg0)
        if match is None or match.group(1) is None:
            ValueError('arg={}'.format(args0))
        form = match.group(1)
        values = list(map(lambda x,c=ctx:self.getRefValue(x, c), args))
        result = form.format(*values)
        return result

