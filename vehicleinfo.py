#! /usr/bin/python3

import logging
import sys
import io

from lib import csvoutput
from lib.strage import Strage
from lib.config import parseArgument, g_config as config 


def getListVehicle(strage, pattern):
    if ':' not in pattern:
        return [ pattern ]
    nation, tier, vtype = pattern.split(':')
    vspec = {}
    if nation == '' or nation == '*':
        vspec['nation'] = None
    else:
        vspec['nation'] = nation.lower().split(',')
    if tier == '' or tier == '*':
        vspec['tier'] = None
    else:
        vspec['tier'] = tier.split(',')
    if vtype == '' or vtype == '*':
        vspec['type'] = None
    else:
        vspec['type'] = vtype.upper().split(',')
    vehicles = strage.getVehicleList(vspec)
    return vehicles


def getVehicleSpec(strage, vid):
    nation = strage.getVehicleNation(vid)
    vspec = {'nation':nation, 'vehicle':vid}
    return vspec

def getVehicleModuleSpecs(strage, vfilter, mfilter):
    vehicles = getListVehicle(strage, vfilter)
    vspecs = [ getVehicleSpec(strage, vid) for vid in vehicles ]
    if mfilter is None:
        mfilter = config.moduleSpecified
    for module in ('chassis', 'turret', 'engine', 'radio', 'gun', 'shell'):
        if module not in mfilter or mfilter[module] is None or mfilter[module] == '*':
            index = None
        elif isinstance(mfilter[module], int):
            index = mfilter[module]
        elif mfilter[module].isdigit() or (mfilter[module][0] == '-' and mfilter[module][1:].isdigit()):
            index = int(mfilter[module])
        else:
            logger.error('bad specified: {}'.format(mspec))
            raise
        newvspecs = []
        for vs in vspecs:
            mlist = strage.getModuleList(vs, module)
            if index is not None:
                mlist = [ mlist[index] ]
            for mid in mlist:
                newvs = vs.copy()
                newvs[module] = mid
                newvspecs.append(newvs)
        vspecs = newvspecs
    return vspecs


def _getVehicleValues(vspecs, tags):
    result = [ strage.getVehicleItemsInfo(vs, tags) for vs in vspecs ]
    return result

def _removeDuplicate(values):
    if config.suppress_unique:
        return values
    result = []
    data = {}
    for v in values:
        k = tuple(v.values())
        if k not in data:
            data[k] = True
            result.append(v)
    return result

def _outputValues(values):
    if config.csvoutput:
        message = csvoutput.createMessageByArrayOfDict(values, not config.suppress_header)
        print(message, end='')
    else:
        for v in values:
            print(v)


class Command:

    @staticmethod
    def listVehicle(strage, pattern):
        for vehicle in getListVehicle(strage, pattern):
            nation = strage.getVehicleNation(vehicle)
            info = strage.getVehicleItemsInfo({'nation':nation, 'vehicle':vehicle}, ['vehicle:index', 'vehicle:userString'])
            print('{:<32} : {}'.format(info['vehicle:index'], info['vehicle:userString']))

    @staticmethod
    def listNation(strage):
        print(', '.join([ v[0] for v in strage.fetchNationList(None, None) ]))

    @staticmethod
    def listTier(strage):
        print(', '.join([ v[0] for v in strage.fetchTierList(None, None) ]))

    @staticmethod
    def listType(strage):
        print(', '.join([ v[0] for v in strage.fetchTypeList(None, None) ]))

    @staticmethod
    def listModule(strage, vfilter, modules, params):
        defaultModule = {
            'chassis':  [ 'chassis' ],
            'turret':   [ 'turret' ],
            'engine':   [ 'engine' ],
            'radio':    [ 'radio' ],
            'gun':      [ 'turret', 'gun' ],
            'shell':    [ 'turret', 'gun', 'shell' ]
        }
        defaultTag = {
            'chassis':  'chassis:index',
            'turret':   'turret:index',
            'engine':   'engine:index',
            'radio':    'radio:index',
            'gun':      'gun:index',
            'shell':    'shell:index'
        }
        mfilter = config.moduleSpecified.copy()
        tags = [ 'vehicle:index' ]
        if ',' not in modules:
            for mname in defaultModule[modules]:
                mfilter[mname] = None
                tags.append(defaultTag[mname])
        else:
            for mname in modules.split(','):
                if mname == '':
                    continue
                mfilter[mname] = None
                tags.append(defaultTag[mname])
        if params is not None:
            tags = params.split(',')
        vspecs = getVehicleModuleSpecs(strage, vfilter, mfilter)
        result = _getVehicleValues(vspecs, tags)
        result = _removeDuplicate(result)
        _outputValues(result)

    @staticmethod
    def infoVehicle(strage, arg, showParams):
        p = arg.split(':')
        nation = strage.getVehicleNation(p[0])
        if len(p) == 7:
            param = { 'nation': nation, 'vehicle': p[0], 'chassis': p[1], 'turret': p[2],
                'engine': p[3], 'radio': p[4], 'gun': p[5], 'shell': p[6] }
        else:
            vehicle = p[0]
            param = { 'nation':nation, 'vehicle':vehicle }
            param['chassis'] = strage.fetchChassisList(None, param)[-1][0]
            param['turret'] = strage.fetchTurretList(None, param)[-1][0]
            param['engine'] = strage.fetchEngineList(None, param)[-1][0]
            param['radio'] = strage.fetchRadioList(None, param)[-1][0]
            param['gun'] = strage.fetchGunList(None, param)[-1][0]
            param['shell'] = strage.fetchShellList(None, param)[0][0]
        if 'siege' not in param:
            param['siege'] = None
        titles, values = strage.getDescription(param)
        if showParams:
            tagList = showParams.split(',')
            result = [ v for v in values if v[0] in tagList ]
        else:
            result = values
        if config.csvoutput:
            if showParams:
                message = csvoutput.createMessage(strage, [titles[0][:2] + sum(result, [])])
            else:
                message = csvoutput.createMessage(strage, titles + result)
            print(message)
        else:
            if showParams:
                for r in result:
                    print('{0[1]:>32}:{0[2]:>6}: {0[3]}'.format(r))
            else:
                for r in titles:
                    print('{0:>33} {1}'.format(r[0], ', '.join(r[1:])))
                for r in result:
                    print('{0[1]:>32}:{0[2]:>6}: {0[3]}'.format(r))
        print(strage.getVehicleItemsInfo(param, tagList))

if __name__ == '__main__':
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s')
    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler())
    
    parseArgument(mode='cui')
    strage = Strage()

    if config.list_nation:
        Command.listNation(strage)
    if config.list_tier:
        Command.listTier(strage)
    if config.list_type:
        Command.listType(strage)
    #if config.pattern:
    #    Command.listVehicle(strage, config.pattern)

    if config.list_module:
        Command.listModule(strage, config.vehicle, config.list_module, config.show_params)

    #if config.vehicle:
    #    Command.infoVehicle(strage, config.vehicle, config.show_params)
