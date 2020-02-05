
from vehicleinfo import _removeEmpty
from lib.vehicles import VehicleDatabase, VehicleSpec, ModuleSpec

from lib.application import g_application as application


def listVehicleModule(vehicles, modules, params, sort=None):
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
    ctxs = application.vd.getVehicleModuleCtx(vehicleSpec, moduleSpec)
    showtags = params.split(',') if params is not None else None
    sorttags = sort.split(',') if sort is not None else None
    tags = set(showtags if showtags is not None else [] + sorttags if sorttags is not None else [])
    result = []    
    for ctx in ctxs:
        result.append(application.vd.getVehicleItems(list(tags), ctx))
    result = _removeDuplicate(result)
    result = _removeEmpty(result)
    result = _sort(result, tags=sorttags)
    return result


def _removeDuplicate(values):
    if application.config.suppress_unique:
        return values
    result = []
    data = {}
    for v in values:
        k = tuple(map(lambda x:repr(x) if isinstance(x, list) else x, v.values()))
        if k not in data:
            data[k] = True
            result.append(v)
    return result


def _sort(records, tags=None):
    if tags is None:
        return records
    keyFuncs = []
    for k in tags:
        schema = application.schema[k]
        func = lambda x,key=k: x[key]
        if 'value' in schema:
            if schema['value'] == 'float':
                func = lambda x,key=k: float(x[key])
        keyFuncs.append(func)
    records = sorted(records, key=lambda x: tuple([ f(x) for f in keyFuncs ]))
    return records
