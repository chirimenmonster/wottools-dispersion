import sys
import io
from lib.strage import Strage
from lib.config import parseArgument, g_config as config 

class Command:

    @staticmethod
    def listVehicle(strage, pattern):
        nation, tier, type = pattern.split(':')
        for r in strage.fetchVehicleList(nation.lower(), tier, type.upper()):
            print('{0[0]:<32} : {0[1]}'.format(r))

    @staticmethod
    def listNation(strage):
        print(', '.join([ v[0] for v in strage.fetchNationList() ]))

    @staticmethod
    def listTier(strage):
        print(', '.join([ v[0] for v in strage.fetchTierList() ]))

    @staticmethod
    def listType(strage):
        print(', '.join([ v[0] for v in strage.fetchTypeList() ]))

    @staticmethod
    def listChassis(strage, vehicle):
        nation = strage.getVehicleNation(vehicle)
        for r in strage.fetchChassisList(nation, vehicle):
            print('{0[0]:<32}: {0[1]}'.format(r))

    @staticmethod
    def listTurret(strage, vehicle):
        nation = strage.getVehicleNation(vehicle)
        for r in strage.fetchTurretList(nation, vehicle):
            print('{0[0]:<32}: {0[1]}'.format(r))

    @staticmethod
    def listEngine(strage, vehicle):
        nation = strage.getVehicleNation(vehicle)
        for r in strage.fetchEngineList(nation, vehicle):
            print('{0[0]:<32}: {0[1]}'.format(r))

    @staticmethod
    def listRadio(strage, vehicle):
        nation = strage.getVehicleNation(vehicle)
        for r in strage.fetchRadioList(nation, vehicle):
            print('{0[0]:<32}: {0[1]}'.format(r))

    @staticmethod
    def listGun(strage, vehicle, turret):
        nation = strage.getVehicleNation(vehicle)
        for r in strage.fetchGunList(nation, vehicle, turret):
            print('{0[0]:<32}: {0[1]}'.format(r))

    @staticmethod
    def listShell(strage, nation, gun):
        for r in strage.fetchShellList(nation, gun):
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
            param['chassis'] = strage.fetchChassisList(nation, vehicle)[-1][0]
            param['turret'] = strage.fetchTurretList(nation, vehicle)[-1][0]
            param['engine'] = strage.fetchEngineList(nation, vehicle)[-1][0]
            param['radio'] = strage.fetchRadioList(nation, vehicle)[-1][0]
            param['gun'] = strage.fetchGunList(nation, vehicle, param['turret'])[-1][0]
            param['shell'] = strage.fetchShellList(nation, param['gun'])[0][0]
        result = []
        result.extend(strage.getVehicleDescription(param))
        result.extend(strage.getVehicleInfo(param))
        for r in result:
            print('{0[0]:>32}: {0[1]}'.format(r))


if __name__ == '__main__':
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
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
