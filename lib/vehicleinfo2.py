
import json

from lib.vehicles import VehicleDatabase, VehicleSpec, ModuleSpec
from lib.application import g_application as app


def listVehicleModule(vehicles, modules, params, sort=None):
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
        else:
            raise ValueError('invalid parameter secret, {}'.format(secrets))
    else:
        secrets = None
    vehicleSpec = VehicleSpec(nations=nations, tiers=tiers, types=types, secrets=secrets)
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
    ctxs = app.vd.getVehicleModuleCtx(vehicleSpec, moduleSpec)
    showtags = params.split(',') if params is not None else []
    sorttags = sort.split(',') if sort is not None else []
    tags = set(showtags + sorttags)
    result = []    
    for ctx in ctxs:
        result.append(app.vd.getVehicleItems(list(tags), ctx))
    result = _removeDuplicate(result)
    result = _removeEmpty(result)
    result = _sort(result, tags=sorttags)
    return result


def _removeDuplicate(values):
    if app.config.suppress_unique:
        return values
    result = []
    data = {}
    for v in values:
        k = tuple(map(lambda x:repr(x) if isinstance(x, list) else x, v.values()))
        if k not in data:
            data[k] = True
            result.append(v)
    return result


def _removeEmpty(records):
    if not app.config.suppress_empty:
        return records
    records = [ r for r in records if None not in r.values() ]
    return records


def _sort(records, tags=None):
    if tags is None:
        return records
    keyFuncs = []
    for k in tags:
        schema = app.settings.schema[k]
        func = lambda x,key=k: x[key]
        if 'value' in schema:
            if schema['value'] == 'int':
                func = lambda x,key=k: int(x[key])
            elif schema['value'] == 'float':
                func = lambda x,key=k: float(x[key])
        keyFuncs.append(func)
    records = sorted(records, key=lambda x: tuple([ f(x) for f in keyFuncs ]))
    return records


def _outputValues(records, show=None):
    showtags = show.split(',') if show is not None else []
    if app.config.csvoutput:
        message = csvoutput.createMessageByArrayOfDict(records, not config.suppress_header)
        print(message, end='')
    elif app.config.outputjson:
        print(json.dumps(records, ensure_ascii=False, indent=2))
    else:
        if len(records) == 0:
            return
        forms = []
        widths = []
        for k in showtags:
            if 'format' in app.settings.schema[k]:
                f = '{!s:' + app.settings.schema[k]['format'] + '}'
            else:
                f = '{!s:>7}'
            forms.append(f)
            widths.append(len(f.format(None)))
        if not app.config.suppress_header:
            if app.config.show_headers:
                tokens = [ f.format(k) for f,w,k in zip(forms, widths, app.config.show_headers.split(',')) ]
                widths = [ len(t) for t in tokens ]
            else:
                tokens = [ f.format(k)[:w] for f,w,k in zip(forms, widths, showtags) ]
            print(' '.join(tokens))
        for r in records:
            values = [ ('{!s:' + str(w) + '}').format(f.format(r[k])) for f,w,k in zip(forms, widths, showtags) ]
            print(' '.join(values))

