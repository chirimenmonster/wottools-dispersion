
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
        schemapath = config.schema
        schema = Settings(schema=schemapath).schema
        vpath = self.setupVPath(config)
        strage = Strage()
        resource = Resource(strage, vpath, schema)
        vd = VehicleDatabase(resource)
        vd.prepare()
        self.vd = vd
        self.resource = resource
        self.schema = schema
        self.config = config
        gettext = Gettext(localedir=config.localedir)
        self.gettext = gettext
        resource.gettext = gettext
        self.dropdownlist = None

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


g_application = Application()
