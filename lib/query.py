
import sys
import json
from collections import namedtuple, OrderedDict

from lib.database import VehicleDatabase, VehicleSpec, ModuleSpec
from lib.stats import VehicleStatsCollection


def queryVehicleModule(app, vehicles, modules, params, sort=None):
    if ':' in vehicles:
        args = vehicles.split(':')
        nations, tiers, types = list(map(lambda x:x.split(','), args[:3]))
        nations = nations if nations != [''] else None 
        tiers = list(map(int, tiers)) if tiers != [''] else None
        types = list(map(lambda x:x.upper(), types)) if types != [''] else None
        if len(args) > 3:
            secrets = args[3]
            if secrets == 'secret':
                secrets = [True]
            elif secrets == 'all':
                secrets = [True, False]
            elif secrets == '':
                secrets = [False]
            else:
                raise ValueError('invalid parameter secret, {}'.format(secrets))
        else:
            secrets = None
        vehicleSpec = VehicleSpec(nations=nations, tiers=tiers, types=types, secrets=secrets)
    else:
        vehicles = vehicles.split(',')
        vehicleSpec = None

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

    showtags = params.split(',') if params is not None else []
    showtags = list(filter(None, showtags))
    unknowntag = list(filter(lambda x: x not in app.settings.schema, showtags))
    if len(unknowntag) > 0:
        sys.stderr.write('unknwon show tags: {}\n'.format(', '.join(map(repr, unknowntag))))
        sys.exit(1)
    sortkeys = sort.split(',') if sort is not None else []
    sortkeys = list(filter(None, sortkeys))
    sorttags = list(map(lambda x:x.strip('-'), sortkeys))
    unknowntag = list(filter(lambda x: x not in app.settings.schema, sorttags))
    if len(unknowntag) > 0:
        sys.stderr.write('unknwon sort tags: {}\n'.format(', '.join(map(repr, unknowntag))))
        sys.exit(1)
    tags = set(showtags + sorttags)

    if vehicleSpec is not None:
        ctxs = app.vd.getVehicleModuleCtx(vehicleSpec, moduleSpec)
    else:
        ctxs = app.vd.getVehicleModuleCtx(vehicles, moduleSpec)
    result = []    
    for ctx in ctxs:
        result.append(app.vd.getVehicleItems(list(tags), ctx))
    result = VehicleStatsCollection(result, schema=app.settings.schema, orderType=app.settings.orders)
    if len(sortkeys):
        result.sort(tags=sortkeys)
    if not app.config.suppress_unique:
        result.removeDuplicate(showtags=showtags)
    if not app.config.suppress_empty:
        result.removeEmpty()
    return result

