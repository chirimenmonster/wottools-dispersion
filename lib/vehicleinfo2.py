
import sys
import json
from collections import namedtuple

from lib.vehicles import VehicleDatabase, VehicleSpec, ModuleSpec
from lib.application import g_application as app


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
    result = _removeDuplicate(result, showtags=showtags)
    result = _removeEmpty(result)
    return result


def _removeDuplicate(values, showtags=None):
    if app.config.suppress_unique:
        return values
    result = []
    data = {}
    for value in values:
        k = tuple(map(lambda x,v=value:repr(v[x]) if isinstance(v[x], list) else v[x], showtags))
        if k not in data:
            data[k] = True
            result.append(value)
    return result


def _removeEmpty(records):
    if not app.config.suppress_empty:
        return records
    records = [ r for r in records if None not in r.values() ]
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
        message = csvoutput.createMessageByArrayOfDict(records, showtags, headers)
        print(message, end='')
    elif app.config.outputjson:
        print(json.dumps(records, ensure_ascii=False, indent=2))
    else:
        if len(records) == 0:
            return
        if headers is None:
            headers = showtags
        RowSchema = namedtuple('RowSchema', 'key type form titleform width func')
        rows = [ None for k in showtags ]
        for i, k in enumerate(showtags):
            form = app.settings.schema[k].get('format', None)
            if form is None:
                type = app.settings.schema[k].get('value', None)
                if type == 'float':
                    form = '.1f'
                elif type == 'int':
                    form = '.0f'
                else:
                    form = 's'
            if 's' in form:
                type = 'str'
                form = '{:' + 's' + '}'
                func = lambda x:x
            elif 'f' in form:
                type = 'float'
                form = '{:' + form + '}'
                func = lambda x:float(x)
            width = max([ len(form.format(func(r[k]))) for r in records ])
            if not app.config.suppress_header:
                width = max(width, len(headers[i]))
            rows[i] = RowSchema(k, type, form, None, width, func)
        for i, r in enumerate(rows):
            titleform = '{:' + str(r.width) + 's}'
            if r.type == 'str':
                form = titleform
            elif r.type == 'float':
                form = r.form.strip('{:}')
                form = '{:' + str(r.width) + form + '}'
            rows[i] = r._replace(form=form, titleform=titleform)
        result = []
        if not app.config.suppress_header:
            tokens = [ r.titleform.format(h) for r,h in zip(rows, headers) ]
            result.append('  '.join(tokens))
        for values in records:
            tokens = [ r.form.format(r.func(values[r.key])) for r in rows ]
            result.append('  '.join(tokens))
        list(map(print, result))
