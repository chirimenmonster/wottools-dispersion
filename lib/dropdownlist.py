
from lib.resources import TIERS, TIERS_LABEL
from lib.application import g_application as app
from lib.vehicles import VehicleSpec, ModuleSpec

class DropdownList(object):

    tags = {
        'chassis':  [ 'chassis:index', 'chassis:userString' ],
        'turret':   [ 'turret:index', 'turret:userString' ],
        'engine':   [ 'engine:index', 'engine:userString' ],
        'radio':    [ 'radio:index', 'radio:userString' ],
        'gun':      [ 'gun:index', 'gun:userString' ],
        'shell':    [ 'shell:index', 'shell:displayString' ]
    }

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

    def fetchSecretList(self, schema=None, param=None):
        return [
            [ "False", "False" ],
            [ "True", "True" ]
        ]

    def fetchVehicleList(self, schema=None, param=None):
        nations = [ param['nation'] ]
        tiers = [ int(param['tier']) ]
        types = [ param['type'] ]
        secret = [ True, False ] if param['secret'] == 'True' else None
        ctxs = app.vd.getVehicleCtx(VehicleSpec(nations, tiers, types, secret))
        tags = [ 'vehicle:index', 'vehicle:userString' ]
        result = [ list(app.vd.getVehicleItems(tags, c).values()) for c in ctxs ]
        return result

    def _fetchModuleList(self, module, param=None):
        vehicle = param['vehicle']
        ctx = app.vd.getCtx(vehicle)
        param = { k:v for k,v in param.items() if k in ModuleSpec._fields}
        ctx.update(param)
        names = app.vd.getModuleList(module, ctx)
        ctxs = []
        for n in names:
            c = ctx.copy()
            c[module] = n
            ctxs.append(c)
        result = [ list(app.vd.getVehicleItems(self.tags[module], c).values()) for c in ctxs ]
        return result

    def fetchChassisList(self, schema=None, param=None):
        param = param.copy()
        result = self._fetchModuleList('chassis', param=param)
        return result

    def fetchTurretList(self, schema=None, param=None):
        result = self._fetchModuleList('turret', param=param)
        return result

    def fetchEngineList(self, schema=None, param=None):
        result = self._fetchModuleList('engine', param=param)
        return result

    def fetchRadioList(self, schema=None, param=None):
        result = self._fetchModuleList('radio', param=param)
        return result

    def fetchGunList(self, schema=None, param=None):
        result = self._fetchModuleList('gun', param=param)
        return result

    def fetchShellList(self, schema=None, param=None):
        result = self._fetchModuleList('shell', param=param)
        return result

