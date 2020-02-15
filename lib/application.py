
import os

from lib.vpath import Strage, VPath, Settings, Resource
from lib.vehicles import VehicleDatabase
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
        settings = self.setupSettings(config)
        schema = settings.schema
        vpath = self.setupVPath(config)
        strage = Strage()
        self.gettext = self.setupGettext(config)
        resource = Resource(strage, vpath, schema, gettext=self.gettext)
        vd = VehicleDatabase(resource)
        vd.prepare()
        self.settings = settings
        self.vd = vd
        self.resource = resource
        self.schema = schema
        self.config = config
        self.dropdownlist = None
        self.settings.orders = { k:resource.getValue(k) for k in ('settings:nationsOrder', 'settings:typesOrder') }

    def setupSettings(self, config):
        if config.schema is None:
            schemapath = 'res/itemschema.json'
        else:
            schemapath = config.schema
        settings = Settings(schema=schemapath)
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
            pkgdir = config.pkg
        scriptsdir = config.SCRIPTS_DIR
        guidir = config.GUI_DIR
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

g_application = Application()
