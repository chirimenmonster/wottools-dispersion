
import sys
import json
from collections import namedtuple, OrderedDict

from lib.vehicles import VehicleDatabase, VehicleSpec, ModuleSpec
from lib.application import g_application as app
from lib.element import Element


def serialize(records):
    return [ { k:v.orig for k,v in r.items() } for r in records ]


def listVehicleModule(vehicles, modules, params, sort=None):
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
    unknowntag = list(filter(lambda x: x not in app.schema, showtags))
    if len(unknowntag) > 0:
        sys.stderr.write('unknwon show tags: {}\n'.format(', '.join(map(repr, unknowntag))))
        sys.exit(1)
    sortkeys = sort.split(',') if sort is not None else []
    sortkeys = list(filter(None, sortkeys))
    sorttags = list(map(lambda x:x.strip('-'), sortkeys))
    unknowntag = list(filter(lambda x: x not in app.schema, sorttags))
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
    result = _sort(result, tags=sortkeys)
    result = [ { k:Element(r[k], app.settings.schema[k]) for k in tags } for r in result ]
    result = _removeDuplicate(result, showtags=showtags)
    result = _removeEmpty(result)
    return result


def _removeDuplicate(records, showtags=None):
    if app.config.suppress_unique:
        return records
    uniqset = OrderedDict()
    for r in records:
        key = tuple(map(lambda x:r[x].value, showtags))
        if key not in uniqset:
            uniqset[key] = r
    return uniqset.values()


def _removeEmpty(records):
    if not app.config.suppress_empty:
        return records
    f = lambda x: x.orig is not None
    g = lambda y: None not in map(f, y.values())
    records = list(filter(g, records))
    return records


def _sort(records, tags=None):
    class _rstr(str):
        def __lt__(self, other):
            return not super(_rstr, self).__lt__(other)
    if tags is None:
        return records
    keyFuncs = []
    for k in tags:
        factor = 1
        if k[0] == '-':
            factor = -1
            k = k[1:]
        schema = app.settings.schema[k]
        if factor == 1:
            func = lambda x,key=k: x[key]
        else:
            func = lambda x,key=k: _rstr(x[key])
        if 'sort' in schema:
            if schema['sort'] in ('settings:nationsOrder', 'settings:typesOrder'):
                indexes = app.resource.getValue(schema['sort'])
                func = lambda x,key=k,ref=indexes,f=factor: ref.index(x[key]) * f
            else:
                raise NotImplementedError('sort={}'.format(schema['sort']))
        elif 'value' in schema:
            if schema['value'] == 'int':
                func = lambda x,key=k,f=factor: int(x[key]) * f if x[key] is not None else float('+inf')
            elif schema['value'] == 'float':
                func = lambda x,key=k,f=factor: float(x[key]) * f if x[key] is not None else float('+inf')
        keyFuncs.append(func)
    records = sorted(records, key=lambda x: tuple([ f(x) for f in keyFuncs ]))
    return records


def _outputValues(records, show=None, headers=None):
    showtags = show.split(',') if show is not None else []
    headers = headers.split(',') if headers is not None else None
    if app.config.csvoutput:
        from lib import csvoutput
        if headers is None:
            headers = showtags
        if app.config.suppress_header:
            headers = None
        message = csvoutput.createMessageByArrayOfDict(serialize(records), showtags, headers)
        print(message, end='')
    elif app.config.outputjson:
        print(json.dumps(serialize(records), ensure_ascii=False, indent=2))
    elif True:
        if len(records) == 0:
            return
        if headers is None:
            headers = showtags
        headers = { k:h for k,h in zip(showtags, headers) }
        rowlen = { k:max([ len(r[k].getFormattedString()) for r in records ]) for k in showtags }
        result = []
        if not app.config.suppress_header:
            rowlen = { k:max(rowlen[k], len(headers[k])) for k in showtags }
            result.append('  '.join([ headers[k].ljust(rowlen[k]) for k in showtags ]))
        for r in records:
            result.append('  '.join([ r[k].getFormattedString(width=rowlen[k]) for k in showtags ]))
        list(map(print, result))
