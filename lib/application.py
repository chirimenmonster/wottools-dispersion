
import os
import json

from lib.vpath import Strage, VPath
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
        if config.localedir is None:
            config.localedir = os.path.join(config.basedir, config.LOCALE_RELPATH)
        if config.schema is None:
            config.schema = 'res/itemschema.json'
        self.settings = self.setupSettings(config)
        self.config = config
        self.schema = self.settings.schema
        vpath = self.setupVPath(config)
        strage = Strage()
        self.gettext = self.setupGettext(config)
        self.resource = Resource(self, strage, vpath, self.schema, gettext=self.gettext)
        self.vd = VehicleDatabase(self.resource)
        self.vd.prepare()
        self.dropdownlist = None
        self.settings.addDict('orders', { k:self.resource.getValue(k) for k in ('settings:nationsOrder', 'settings:typesOrder') })

    def setupSettings(self, config):
        if config.schema is None:
            schemapath = 'res/itemschema.json'
        else:
            schemapath = config.schema
        settings = Settings()
        settings.add('schema', schemapath)
        if config.gui:
            settings.add('guiitems', 'res/guisettings_items.json')
            settings.add('guititles', 'res/guisettings_titles.json')
            settings.add('guiselectors', 'res/guisettings_selectors.json')
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
        vpath = VPath(pkgdir=pkgdir, scriptsdir=scriptsdir, guidir=guidir, scriptspkg=scriptspkg)
        return vpath

    def setupGettext(self, config):
        if config.localedir is None:
            pkgdir = '/'.join([config.basedir, config.LOCALE_RELPATH])
        gettext = Gettext(localedir=config.localedir)
        return gettext

    def setupGuiConfig(self, config):
        with open(self.guisettings_items, 'r') as fp:
            self.itemgroup = json.load(fp)
        with open('res/guisettings_titles.json', 'r') as fp:
            self.titlesdesc = json.load(fp)
        with open('res/guisettings_selectors.json', 'r') as fp:
            self.selectorsdesc = json.load(fp)


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


g_application = Application()
