#! /usr/bin/python3

import logging
import os
import sys
import io
import re

from lib.config import parseArgument, g_config as config 
from lib.application import g_application as app
from lib.query import queryVehicleModule
from lib.output import outputValues


defaultargs = {
    'empty': {
        'show':     'vehicle:nation,vehicle:tier,vehicle:type,vehicle:id,vehicle:index,vehicle:userString',
        'sort':     'vehicle:nation,vehicle:tier,vehicle:type,vehicle:id',
        'header':   'Nation,Tier,Type,Id,Index,UserString'
    },
    'secret': {
        'show':     'vehicle:nation,vehicle:tier,vehicle:type,vehicle:secret,vehicle:id,vehicle:index,vehicle:userString',
        'sort':     'vehicle:nation,vehicle:tier,vehicle:type,vehicle:id',
        'header':   'Nation,Tier,Type,Secret,Id,Index,UserString'
    },
    'chassis': {
        'show':     'vehicle:index,chassis:index',
        'sort':     'vehicle:nation,vehicle:tier,vehicle:type,vehicle:id',
        'header':   'Vehicle,Chassis'
    },
    'engine': {
        'show':     'vehicle:index,engine:index',
        'sort':     'vehicle:nation,vehicle:tier,vehicle:type,vehicle:id',
        'header':   'Vehicle,Engine'
    },
    'radio': {
        'show':     'vehicle:index,radio:index',
        'sort':     'vehicle:nation,vehicle:tier,vehicle:type,vehicle:id',
        'header':   'Vehicle,Radio'
    },
    'turret': {
        'show':     'vehicle:index,turret:index',
        'sort':     'vehicle:nation,vehicle:tier,vehicle:type,vehicle:id',
        'header':   'Vehicle,Turret'
    },
    'gun': {
        'show':     'vehicle:index,turret:index,gun:index',
        'sort':     'vehicle:nation,vehicle:tier,vehicle:type,vehicle:id',
        'header':   'Vehicle,Turret,Gun'
    },
    'shell': {
        'show':     'vehicle:index,turret:index,gun:index,shell:index',
        'sort':     'vehicle:nation,vehicle:tier,vehicle:type,vehicle:id',
        'header':   'Vehicle,Turret,Gun,Shell'
    }
}



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
        vehicles = config.list_vehicle
        modules = config.list_module
        showtags = config.show_params
        headers = config.show_headers
        sorttags = config.sort
        if showtags is None:
            if len(vehicles.split(':')) == 4:
                default = defaultargs.get(modules, defaultargs['secret'])
            else:
                default = defaultargs.get(modules, defaultargs['empty'])                
            showtags = default['show']
            if sorttags is None:
                sorttags = default['sort']
            if headers is None:
                headers = default['header']
        result = queryVehicleModule(app, vehicles, modules, showtags, sort=sorttags)
        outputValues(result, shows=showtags, headers=headers, option=config)
    elif config.list_tag:
        result = app.schema.keys()
        def f(pattern, string):
            match = re.search(pattern, string)
            return match
        result = filter(lambda x,p=config.list_tag: f(p, x), result)
        for r in result:
            print(r)
    else:
        raise ValueError
