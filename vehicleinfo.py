#! /usr/bin/python3

import logging
import os
import sys
import io
import json

from lib import csvoutput
from lib.config import parseArgument, g_config as config 
from lib.application import g_application as app
from lib.vehicleinfo2 import listVehicleModule, _outputValues


class Command:
        
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

    app.setup(config)
    if config.list_nation:
        result = app.resource.getValue('settings:nationsOrder')
        print(result)
    elif config.list_tier:
        result = app.resource.getValue('settings:tiersOrder')
        print(result)
    elif config.list_type:
        result = app.resource.getValue('settings:typesOrder')
        print(result)    
    elif config.list_vehicle:
        showtag = config.show_params
        headers = config.show_headers
        sorttag = config.sort
        if showtag is None:
            if config.list_module is None:
                showtag = 'vehicle:nation,vehicle:tier,vehicle:type,vehicle:secret,vehicle:id,vehicle:index,vehicle:userString'
                if sorttag is None:
                    sorttag = 'vehicle:nation,vehicle:tier,vehicle:type,vehicle:id'
                if headers is None:
                    headers = 'Nation,Tier,Type,Secret,Id,Index,UserString'
            elif config.list_module == 'turret':
                showtag = 'vehicle:index,turret:index'
                if sorttag is None:
                    sorttag = 'vehicle:nation,vehicle:tier,vehicle:type,vehicle:id'
                if headers is None:
                    headers = 'Vehicle,Turret'
            elif config.list_module == 'gun':
                showtag = 'vehicle:index,turret:index,gun:index'
                if sorttag is None:
                    sorttag = 'vehicle:nation,vehicle:tier,vehicle:type,vehicle:id'
                if headers is None:
                    headers = 'Vehicle,Turret,Gun'
            elif config.list_module == 'shell':
                showtag = 'vehicle:index,turret:index,gun:index,shell:index'
                if sorttag is None:
                    sorttag = 'vehicle:nation,vehicle:tier,vehicle:type,vehicle:id'
                if headers is None:
                    headers = 'Vehicle,Turret,Gun,Shell'
        
        result = listVehicleModule(config.list_vehicle, config.list_module, showtag, sort=sorttag)
        _outputValues(result, show=showtag, headers=headers)
    else:
        raise ValueError
