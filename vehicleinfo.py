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
    vspec = { 'nation':nation, 'vehicle':vid }
    return vspec

def getDefaultVehicleSpec(strage, vid, mspec):
    vspec = getVehicleSpec(strage, vid)
    if mspec is not None:
        vspec.update(mspec)
    for name in ('chassis', 'turret', 'engine', 'radio', 'gun', 'shell'):
        if name not in vspec:
            array = strage.getModuleList(vspec, name)
            vspec[name] = array[config.moduleSpecified[name]]
    return vspec


def _listSimpleModule(strage, vfilter, module):
    if module not in ['chassis', 'turret', 'engine', 'radio']:
        raise ValueError('not support as simple module: "{}"'.format(module))
    vehicles = getListVehicle(strage, vfilter)
    vspecs = []
    for vid in vehicles:
        vs = getVehicleSpec(strage, vid)
        mlist = strage.getModuleList(vs, module)
        for mid in mlist:
            vs[module] = mid
            vspecs.append(vs.copy())
    return vspecs

def _listGun(strage, vfilter):
    oldvspecs = _listSimpleModule(strage, vfilter, 'turret')
    vspecs = []
    for vs in oldvspecs:
        guns = strage.getModuleList(vs, 'gun')
        for gid in guns:
            vs['gun'] = gid
            vspecs.append(vs.copy())
    return vspecs

def _listShell(strage, vfilter):
    oldvspecs = _listGun(strage, vfilter)
    vspecs = []
    for vs in oldvspecs:
        shells = strage.getModuleList(vs, 'shell')
        for sid in shells:
            vs['shell'] = sid
            vspecs.append(vs.copy())
    return vspecs


def _getVehicleValues(vspecs, tags):
    result = [ strage.getVehicleItemsInfo(vs, tags) for vs in vspecs ]
    return result
    
def _outputValues(values):
    if config.csvoutput:
        message = csvoutput.createMessageByArrayOfDict(values)
        print(message)
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
    def listChassis(strage, vfilter, params):
        tags = params.split(',') if params else ['vehicle:index', 'chassis:index']
        vspecs = _listSimpleModule(strage, vfilter, 'chassis')
        result = _getVehicleValues(vspecs, tags)
        _outputValues(result)

    @staticmethod
    def listTurret(strage, vfilter, params):
        tags = params.split(',') if params else ['vehicle:index', 'turret:index']
        vspecs = _listSimpleModule(strage, vfilter, 'turret')
        result = _getVehicleValues(vspecs, tags)
        _outputValues(result)

    @staticmethod
    def listEngine(strage, vfilter, params):
        tags = params.split(',') if params else ['vehicle:index', 'engine:index']
        vspecs = _listSimpleModule(strage, vfilter, 'engine')
        result = _getVehicleValues(vspecs, tags)
        _outputValues(result)

    @staticmethod
    def listRadio(strage, vfilter, params):
        tags = params.split(',') if params else ['vehicle:index', 'radio:index']
        vspecs = _listSimpleModule(strage, vfilter, 'radio')
        result = _getVehicleValues(vspecs, tags)
        _outputValues(result)

    @staticmethod
    def listGun(strage, vfilter, showParams):
        vspecs = _listGun(strage, vfilter)
        if showParams:
            tags = showParams.split(',')
        else:
            tags = [ 'vehicle:index', 'gun:index' ]
        result = [ strage.getVehicleItemsInfo(vs, tags) for vs in vspecs ]
        if config.csvoutput:
            message = csvoutput.createMessageByArrayOfDict(result)
            print(message)
        else:
            for r in result:
                print(r)

    @staticmethod
    def listShell(strage, vfilter, showParams):
        oldvspecs = _listShell(strage, vfilter)
        vspecs = []
        vdict = {}
        for vs in oldvspecs:
            uid = (vs['vehicle'], vs['gun'])
            if uid in vdict:
                continue
            vdict[uid] = True
            vspecs.append(vs)
        if showParams:
            tags = showParams.split(',')
        else:
            tags = [ 'vehicle:index', 'gun:index', 'shell:index' ]
        result = [ strage.getVehicleItemsInfo(vs, tags) for vs in vspecs ]
        if config.csvoutput:
            message = csvoutput.createMessageByArrayOfDict(result)
            print(message)
        else:
            for r in result:
                print(r)
  
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
    
    parseArgument(mode='test')
    strage = Strage()

    if config.list_nation:
        Command.listNation(strage)
    if config.list_tier:
        Command.listTier(strage)
    if config.list_type:
        Command.listType(strage)
    if config.pattern:
        Command.listVehicle(strage, config.pattern)

    if config.vehicle_chassis:
        Command.listChassis(strage, config.vehicle_chassis, config.show_params)
    if config.vehicle_turret:
        Command.listTurret(strage, config.vehicle_turret, config.show_params)
    if config.vehicle_engine:
        Command.listEngine(strage, config.vehicle_engine, config.show_params)
    if config.vehicle_radio:
        Command.listRadio(strage, config.vehicle_radio, config.show_params)
    if config.vehicle_gun:
        Command.listGun(strage, config.vehicle_gun, config.show_params)
    if config.gun_shell:
        Command.listShell(strage, config.gun_shell, config.show_params)

    if config.vehicle:
        Command.infoVehicle(strage, config.vehicle, config.show_params)
