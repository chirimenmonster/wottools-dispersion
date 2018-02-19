import logging
import sys
import io

from lib import csvoutput
from lib.strage import Strage
from lib.config import parseArgument, g_config as config 

class Command:

    @staticmethod
    def listVehicle(strage, pattern):
        nation, tier, type = pattern.split(':')
        param = { 'nation':nation.lower(), 'tier':tier, 'type':type.upper() }
        for r in strage.fetchVehicleList(None, param):
            print('{0[0]:<32} : {0[1]}'.format(r))

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
    def listChassis(strage, vehicle):
        nation = strage.getVehicleNation(vehicle)
        param = { 'nation':nation, 'vehicle':vehicle }
        for r in strage.fetchChassisList(None, param):
            print('{0[0]:<32}: {0[1]}'.format(r))

    @staticmethod
    def listTurret(strage, vehicle):
        nation = strage.getVehicleNation(vehicle)
        param = { 'nation':nation, 'vehicle':vehicle }
        for r in strage.fetchTurretList(None, param):
            print('{0[0]:<32}: {0[1]}'.format(r))

    @staticmethod
    def listEngine(strage, vehicle):
        nation = strage.getVehicleNation(vehicle)
        param = { 'nation':nation, 'vehicle':vehicle }
        for r in strage.fetchEngineList(None, param):
            print('{0[0]:<32}: {0[1]}'.format(r))

    @staticmethod
    def listRadio(strage, vehicle):
        nation = strage.getVehicleNation(vehicle)
        param = { 'nation':nation, 'vehicle':vehicle }
        for r in strage.fetchRadioList(None, param):
            print('{0[0]:<32}: {0[1]}'.format(r))

    @staticmethod
    def listGun(strage, vehicle, turret):
        nation = strage.getVehicleNation(vehicle)
        param = { 'nation':nation, 'vehicle':vehicle, 'turret':turret }
        for r in strage.fetchGunList(None, param):
            print('{0[0]:<32}: {0[1]}'.format(r))

    @staticmethod
    def listShell(strage, nation, gun):
        param = { 'nation':nation, 'gun':gun }
        for r in strage.fetchShellList(None, param):
            print('{0[0]:<32}: {0[1]}'.format(r))


    @staticmethod
    def infoVehicle(strage, arg):
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
        if config.csvoutput:
            message = csvoutput.createMessage(strage, titles + values)
            print(message)
        else:
            for r in titles:
                print('{0:>33} {1}'.format(r[0], ', '.join(r[1:])))
            for r in values:
                print('{0[1]:>32}:{0[2]:>6}: {0[3]}'.format(r))

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
        Command.listChassis(strage, config.vehicle_chassis)
    if config.vehicle_turret:
        Command.listTurret(strage, config.vehicle_turret)
    if config.vehicle_engine:
        Command.listEngine(strage, config.vehicle_engine)
    if config.vehicle_radio:
        Command.listRadio(strage, config.vehicle_radio)
    if config.vehicle_gun:
        Command.listGun(strage, *config.vehicle_gun.split(':'))
    if config.gun_shell:
        Command.listShell(strage, *config.gun_shell.split(':'))

    if config.vehicle:
        Command.infoVehicle(strage, config.vehicle)
