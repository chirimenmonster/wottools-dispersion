
from lib.vpath import Strage, VPath, Settings, Resource

class Application(object):

    def setup(self, config):
        schemapath = config.schema
        pkgdir = config.pkgdir
        scriptsdir = config.SCRIPTS_DIR
        guidir = config.GUI_DIR
        scriptspkg = config.scriptspkg
        schema = Settings(schema=schemapath).schema
        strage = Strage()
        vpath = VPath(pkgdir=pkgdir, scriptsdir=scriptsdir, guidir=guidir, scriptspkg=scriptspkg)
        self.resource = Resource(strage, vpath, schema)
        self.schema = schema

g_application = Application()
