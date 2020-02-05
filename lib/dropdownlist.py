
from lib.resources import TIERS, TIERS_LABEL
from lib.application import g_application as app
from lib.vehicles import VehicleSpec

class DropdownList(object):

    def fetchNationList(self, schema=None, param=None):
        self.nationsOrder = app.resource.getValue('settings:nationsOrder')
        result = [ [s, s.upper()] for s in self.nationsOrder ]
        return result

    def fetchTierList(self, schema=None, param=None):
        return [ [ tier, TIERS_LABEL[tier] ] for tier in TIERS ]

    def fetchTypeList(self, schema=None, param=None):
        typesOrder = app.resource.getValue('settings:typesOrder')
        result = [ [ type, type ] for type in typesOrder ]
        return result

    def fetchVehicleList(self, schema=None, param=None):
        nations = [ param['nation'] ]
        tiers = [ int(param['tier']) ]
        types = [ param['type'] ]
        ctxs = app.vd.getVehicleCtx(VehicleSpec(nations, tiers, types))
        tags = [ 'vehicle:index', 'vehicle:userString' ]
        result = [ app.vd.getVehicleItems(tags, c._asdict()).values() for c in ctxs ]
        return result
