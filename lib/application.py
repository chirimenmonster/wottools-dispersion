
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
        schema = self.setupItemschema(config)
        vpath = self.setupVPath(config)
        strage = Strage()
        self.gettext = self.setupGettext(config)
        resource = Resource(strage, vpath, schema, gettext=self.gettext)
        vd = VehicleDatabase(resource)
        vd.prepare()
        self.vd = vd
        self.resource = resource
        self.schema = schema
        self.config = config
        self.dropdownlist = None

    def setupItemschema(self, config):
        schemapath = config.schema
        schema = Settings(schema=schemapath).schema
        return schema
    
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


g_application = Application()
