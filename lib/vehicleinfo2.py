
from vehicleinfo import _removeDuplicate, _removeEmpty, _sort
from lib.vehicles import VehicleDatabase, VehicleSpec, ModuleSpec, getResource
from lib.config import parseArgument, g_config as config 

def listVehicleModule(vehicles, modules, params):
    nations, tiers, types = map(lambda x:x.split(','), vehicles.split(':'))
    nations = nations if nations != [''] else None 
    tiers = list(map(int, tiers)) if tiers != [''] else None
    types = list(map(lambda x:x.upper(), types)) if types != [''] else None
    vehicleSpec = VehicleSpec(nations=nations, tiers=tiers, types=types)
    defaultModule = {
        'chassis':  [ 'chassis' ],
        'turret':   [ 'turret' ],
        'engine':   [ 'engine' ],
        'radio':    [ 'radio' ],
        'gun':      [ 'turret', 'gun' ],
        'shell':    [ 'turret', 'gun', 'shell' ]
    }
    moduleSpec = ModuleSpec()
    if modules is not None:
        for mname in modules.split(','):
            for m in defaultModule[mname]:
                d = {m: None}
                moduleSpec = moduleSpec._replace(**d)
    vd = VehicleDatabase(getResource(config))
    vd.prepare()
    ctxs = vd.getVehicleModuleCtx(vehicleSpec, moduleSpec)
    result = []
    if params is not None:
        tags = params.split(',')
    for ctx in ctxs:
        result.append(vd.getVehicleItems(tags, ctx))
    result = _removeDuplicate(result)
    result = _removeEmpty(result)
    result = _sort(result)
    return result
