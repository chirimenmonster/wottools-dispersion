
from lib.query import VehicleSpec, ModuleSpec


class DropdownList(object):

    tags = {
        'chassis':  [ 'chassis:index', 'chassis:userString' ],
        'turret':   [ 'turret:index', 'turret:userString' ],
        'engine':   [ 'engine:index', 'engine:userString' ],
        'radio':    [ 'radio:index', 'radio:userString' ],
        'gun':      [ 'gun:index', 'gun:userString' ],
        'shell':    [ 'shell:index', 'shell:displayString' ]
    }

    def __init__(self, app):
        self.app = app
    
    def fetchNationList(self, schema=None, param=None):
        self.nationsOrder = self.app.resource.getValue('settings:nationsOrder')
        result = [ [s, s.upper()] for s in self.nationsOrder ]
        return result

    def fetchTierList(self, schema=None, param=None):
        tiersOrder = self.app.resource.getValue('settings:tiersOrder')
        tiersLabel = self.app.resource.getValue('settings:tiersLabel')
        return [ [ tier, tiersLabel[tier] ] for tier in map(str, tiersOrder) ]

    def fetchTypeList(self, schema=None, param=None):
        typesOrder = self.app.resource.getValue('settings:typesOrder')
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
        secret = [ True, False ] if param.get('secret', None) == 'True' else None
        ctxs = self.app.vd.getVehicleCtx(VehicleSpec(nations, tiers, types, secret))
        tags = [ 'vehicle:index', 'vehicle:userString' ]
        result = [ list(self.app.vd.getVehicleItems(tags, c).values()) for c in ctxs ]
        return result

    def _fetchModuleList(self, module, param=None):
        vehicle = param['vehicle']
        ctx = self.app.vd.getCtx(vehicle)
        param = { k:v for k,v in param.items() if k in ModuleSpec._fields}
        ctx.update(param)
        names = self.app.vd.getModuleList(module, ctx)
        ctxs = []
        for n in names:
            c = ctx.copy()
            c[module] = n
            ctxs.append(c)
        result = [ list(self.app.vd.getVehicleItems(self.tags[module], c).values()) for c in ctxs ]
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

