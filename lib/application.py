
import os
import json

from lib.vpath import VPath
from lib.strage import Strage
from lib.resource import Resource
from lib.database import VehicleDatabase
from lib.translate import Gettext


def guessBasedir():
    BASE_DIRS = [ 'C:/Games/World_of_Tanks', 'C:/Games/World_of_Tanks_ASIA' ]
    basedir = None
    for d in BASE_DIRS:
        if os.path.isdir(d):
            basedir = d
            break
    return basedir


class Application(object):

    def setup(self, config):
        if config.basedir is None:
            config.basedir = guessBasedir()
        self.config = config
        self.settings = self.setupSettings(config)
        self.gettext = self.setupGettext(config)
        self.resource = self.setupResource(config, schema=self.settings.schema, gettext=self.gettext)
        self.vd = self.setupDatabase(resource=self.resource)

        orders = ('settings:nationsOrder', 'settings:tiersOrder', 'settings:typesOrder', 'settings:tiersLabel')
        self.settings.addDict('orders', { k:self.resource.getValue(k) for k in orders })
        if config.gui:
            self.dropdownlist = None

    def setupSettings(self, config):
        scriptpath = os.path.join(os.path.dirname(__file__), '..')
        if config.schema is None:
            schemapath = os.path.join(scriptpath, 'res/itemschema.json')
        else:
            if config.schema is not None and not os.path.isfile(config.schema):
                raise FileNotFoundError('not found schema file: {}'.format(config.schema))
            schemapath = config.schema
        settings = Settings()
        settings.add('schema', schemapath)
        if config.gui:
            settings.add('guiitems', os.path.join(scriptpath, 'res/guisettings_items.json'))
            settings.add('guititles', os.path.join(scriptpath, 'res/guisettings_titles.json'))
            settings.add('guiselectors', os.path.join(scriptpath, 'res/guisettings_selectors.json'))
        return settings
        
    def setupVPath(self, config):
        if config.pkgdir is None:
            if config.basedir:
                pkgdir = '/'.join([config.basedir, config.PKG_RELPATH])
            else:
                pkgdir = None
        else:
            pkgdir = config.pkgdir
        scriptsdir = config.scriptsdir
        guidir = config.guidir
        scriptspkg = config.scriptspkg
        guipkg = config.guipkg
        if pkgdir is not None and not os.path.isdir(pkgdir):
            raise FileNotFoundError('not found pkgdir: {}'.format(pkgdir))
        if scriptsdir is not None and not os.path.isdir(scriptsdir):
            raise FileNotFoundError('not found scriptsdir: {}'.format(scriptsdir))
        if guidir is not None and not os.path.isdir(guidir):
            raise FileNotFoundError('not found guidir: {}'.format(guidir))
        if scriptspkg is not None and not os.path.isfile(scriptspkg):
            raise FileNotFoundError('not found scriptspkg: {}'.format(scriptspkg))
        if guipkg is not None and not os.path.isfile(guipkg):
            raise FileNotFoundError('not found guipkg: {}'.format(guipkg))
        vpath = VPath(pkgdir=pkgdir, scriptsdir=scriptsdir, guidir=guidir, scriptspkg=scriptspkg, guipkg=guipkg)
        return vpath

    def setupGettext(self, config):
        if config.localedir is None:
            localedir = os.path.join(config.basedir, config.LOCALE_RELPATH)
        else:
            localedir = config.localedir
        if not os.path.isdir(localedir):
            raise FileNotFoundError('not found localedir: {}'.format(localedir))
        gettext = Gettext(localedir=localedir)
        return gettext

    def setupResource(self, config, schema=None, gettext=None):
        vpath = self.setupVPath(config)
        strage = Strage()
        resource = Resource(app=self, strage=strage, vpath=vpath, schema=schema, gettext=gettext)
        return resource

    def setupDatabase(self, resource=None):
        vd = VehicleDatabase()
        vd.setup(resource)
        return vd


class Settings(object):

    def load(self, path):
        with open(path, 'r') as fp:
            result = json.load(fp)
        return result

    def add(self, name, path):
        with open(path, 'r') as fp:
            result = json.load(fp)
        setattr(self, name, result)
        return self

    def addDict(self, name, dict):
        setattr(self, name, dict)
        return self
