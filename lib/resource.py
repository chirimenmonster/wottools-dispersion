
import re
import logging
import traceback

from lib.itemresource import ResourceFactory
from lib.itemmap import MapFactory
from lib.itemtype import TypeFactory

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Resource(object):

    def __init__(self, app=None, strage=None, vpath=None, schema=None, gettext=None):
        self.__app = app
        self.__strage = strage
        self.__vpath = vpath
        self.__schema = schema
        self.__gettext = gettext
        self.resourceFactory = ResourceFactory(app)
        self.mapFactory = MapFactory(app)
        self.typeFactory = TypeFactory(app)

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

    def getValue(self, tag=None, ctx=None, resources=None, type=None, map=None):
        typedesc, mapdesc = type, map
        if tag is not None:
            schema = self.__schema[tag]
            if resources is None:
                resources = schema.get('resources', None)
            if typedesc is None:
                typedesc = schema.get('value', None)
            if mapdesc is None:
                mapdesc = schema.get('map', None)
        sources = []
        for desc in resources:
            sources.append(self.resourceFactory.create(desc))
        converter = self.typeFactory.create(typedesc)
        mapper = self.mapFactory.create(mapdesc)
        for src in sources:
            try:
                value = src.getValue(ctx)
            except KeyError as e:
                raise KeyError('{}, resources={}, ctx={}'.format(e.args, resources, ctx)) from e
            if value is not None and value is not []:
                break
        value = converter.getValue(value)
        value = mapper.getValue(value)
        return value

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

