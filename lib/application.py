
from lib.vpath import Strage, VPath, Settings, Resource
from lib.vehicles import VehicleDatabase
from lib.translate import g_gettext

class Application(object):

    def setup(self, config):
        schemapath = config.schema
        pkgdir = config.pkgdir
        scriptsdir = config.SCRIPTS_DIR
        guidir = config.GUI_DIR
        scriptspkg = config.scriptspkg
        g_gettext.localedir = config.localedir
        schema = Settings(schema=schemapath).schema
        strage = Strage()
        vpath = VPath(pkgdir=pkgdir, scriptsdir=scriptsdir, guidir=guidir, scriptspkg=scriptspkg)
        resource = Resource(strage, vpath, schema)
        vd = VehicleDatabase(resource)
        vd.prepare()
        self.vd = vd
        self.resource = resource
        self.schema = schema
        self.config = config

        if g_gettext.localedir is None:
            g_gettext.localedir = '/'.join([ config.BASE_DIR, config.LOCALE_RELPATH ])
        
g_application = Application()
