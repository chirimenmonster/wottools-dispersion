
import logging
import os
import io
import re
import json
import zipfile
from collections import namedtuple
import string

import traceback

from lib.config import TIERS_LABEL

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)




class Resource(object):

    def __init__(self, strage, vpath, schema, gettext=None):
        self.__strage = strage
        self.__vpath = vpath
        self.__schema = schema
        self.__gettext = gettext
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

    def findNodes(self, root, xpath):
        result = root.findall(xpath)
        result = list(filter(lambda x:x.tag != 'xmlns:xmlref', result))
        return result

    def resolveXPath(self, root, xpath):
        match = re.fullmatch(r'([^()]*)\((.*)\)', xpath)
        if match:
            fname = match.group(1)
            xpath = match.group(2)
            if fname == 'name':
                result = self.findNodes(root, xpath)
                result = [ r.tag for r in result ]
            elif fname == 'position':
                submatch = re.fullmatch(r'(.*/)([^/]+)', xpath)
                if submatch:
                    xpath = submatch.group(1) + '*'
                    nname = submatch.group(2)
                else:
                    xpath, nname = '*', xpath
                result = self.findNodes(root, xpath)
                result = [ r.tag for r in result ]
                try:
                    result = [ result.index(nname) + 1 ]
                except:
                    print('xpath={}, nname={}'.format(xpath, nname))
                    raise
            else:
                raise NotImplementedError('unknown function: {}, xpath={}'.format(fname, xpath))
        else:
            result = self.findNodes(root, xpath)
            result = [ r.text for r in result ]
        return result

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
        if file is None or xpath is None:
            return None
        path = self.__vpath.getPathInfo(file)
        root = self.__strage.readXml(path)
        return self.resolveXPath(root, xpath)

    def getNodes(self, resources=None, ctx=None):
        for r in resources:
            if 'file' in r and 'xpath' in r:
                file = r['file']
                xpath = r['xpath']
                param = r.get('param', None)
                try:
                    result = self.getFromFile(file, xpath, param, ctx)
                except FileNotFoundError or KeyError:
                    result = None
                if result is None:
                    if r == resources[-1]:
                        break
                elif len(result) > 0:
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
            raise KeyError('{}, resources={}, ctx={}'.format(e.args, resources, ctx)) from e
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
        if result is None:
            return None
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
            for p in list(string.Formatter().parse(value)):
                k = p[1]
                if k is not None:
                    if k not in ctx:
                        raise KeyError('no key "{}" in ctx={}'.format(k, ctx))
                    elif ctx[k] is None:
                        return None
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
        elif datatype in ['float', 'int']:
            if len(value) == 0:
                value = None
            elif len(value) == 1:
                value = value[0]
            else:
                raise ValueError('data type "float" or "int" must one value: {}'.format(value))
        elif datatype in ['list', 'dict']:
            pass
        else:
            raise NotImplementedError('value: {}'.format(datatype))
        return value

    def assignMap(self, value, rule):
        if value is None:
            return None
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
        values = list(map(lambda x,c=ctx:self.getRefValue(x, c), args))
        if None in values:
            return None
        values = map(float, values)
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

