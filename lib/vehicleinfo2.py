
from vehicleinfo import _removeDuplicate, _removeEmpty, _sort
from lib.vehicles import VehicleDatabase, VehicleSpec, ModuleSpec, getResource
from lib.config import parseArgument, g_config as config 

g_schema = None

def listVehicleModule(vehicles, modules, params, sort=None):
    global g_schema
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
    resources, schema = getResource(config)
    g_schema = schema
    vd = VehicleDatabase(resources)
    vd.prepare()
    ctxs = vd.getVehicleModuleCtx(vehicleSpec, moduleSpec)
    showtags = params.split(',') if params is not None else None
    sorttags = sort.split(',') if sort is not None else None
    tags = set(showtags if showtags is not None else [] + sorttags if sorttags is not None else [])
    result = []    
    for ctx in ctxs:
        result.append(vd.getVehicleItems(list(tags), ctx))
    result = _removeDuplicate(result)
    result = _removeEmpty(result)
    result = _sort(result, tags=sorttags)
    return result


def _sort(records, tags=None):
    if tags is None:
        return records
    keyFuncs = []
    for k in tags:
        schema = g_schema[k]
        func = lambda x,key=k: x[key]
        if 'sort' in schema:
            if schema['sort'] == 'float':
                func = lambda x,key=k: float(x[key])
        keyFuncs.append(func)
    records = sorted(records, key=lambda x: tuple([ f(x) for f in keyFuncs ]))
    return records
