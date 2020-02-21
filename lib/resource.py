
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
from lib.resourcefactory import ResourceFactory
from lib.itemmap import MapFactory

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Resource(object):

    def __init__(self, app, strage, vpath, schema, gettext=None):
        self.__app = app
        self.__strage = strage
        self.__vpath = vpath
        self.__schema = schema
        self.__gettext = gettext

    @property
    def gettext(self):
        return self.__gettext
        
    @gettext.setter
    def gettext(self, obj):
        self.__gettext = obj

    @property
    def strage(self):
        return self.__strage
        
    @property
    def vpath(self):
        return self.__vpath

    def getNodes(self, resources=None, ctx=None):
        factory = ResourceFactory(self.__app)
        res = []
        for desc in resources:
            res.append(factory.create(desc))
        result = None
        for r in res:
            result = r.getValue(ctx)
            if result is not None and result is not []:
                break
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

    def assignMap2(self, value, rule):
        obj = MapFactory(app).create(rule)
        result = obj.getValue(value)
        return result

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

