from itertools import product
import re
import json

class Config:
    BASE_DIR = 'C:/Games/World_of_Tanks'
    PKG_RELPATH = 'res/packages'
    LOCALE_RELPATH = 'res'
    VEHICLES = 'vehicles'
    GUI_SETTINGS = 'gui_settings'
    DATA = {
        VEHICLES: {
            'vpath':        'scripts/item_defs/vehicles',
            'packed':       'scripts.pkg',
            'extracted':    None
        },
        GUI_SETTINGS: {
            'vpath':        'gui/gui_settings.xml',
            'packed':       'gui.pkg',
            'extracted':    None
        }
    }

config = Config()

NATIONS = [ 'germany', 'ussr', 'usa', 'uk', 'france', 'china', 'japan', 'czech', 'sweden', 'poland' ]

TIERS = [ str(tier) for tier in range(1, 10 + 1) ]
TIERS_LABEL = { '1':'I', '2':'II', '3':'III', '4':'IV', '5':'V', '6':'VI', '7':'VII', '8':'VIII', '9':'IX', '10':'X'}
TIERS_LIST = [ TIERS_LABEL[t] for t in TIERS ]

TYPES = [ 'lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG' ]
TYPES_LABEL = { 'lightTank':'LT', 'mediumTank':'MT', 'heavyTank':'HT', 'AT-SPG':'TD', 'SPG':'SPG' }
TYPES_LIST = [ TYPES_LABEL[t] for t in TYPES ]


class Translate(object):
    __gettext = {}
    
    def translate(self, text):   
        import gettext
        
        if text is None:
            return ''
        if not text[0] == '#':
            return text
        domain, name = text[1:].split(':')
        if domain not in self.__gettext:
            localedir = '/'.join([ config.BASE_DIR, config.LOCALE_RELPATH ])
            self.__gettext[domain] = gettext.translation(domain, languages=['text'], localedir=localedir, fallback=True)
        if isinstance(self.__gettext[domain], gettext.GNUTranslations):
            return self.__gettext[domain].gettext(name)
        return text

translate = Translate().translate


def readXmlData(domain, target=None):
    import io
    import zipfile
    from XmlUnpacker import XmlUnpacker
    
    xmlunpacker = XmlUnpacker()
    vpath = config.DATA[domain]['vpath'] + ('/' + target if target else '')

    if config.DATA[domain]['extracted']:
        path = '/'.join([ config.DATA[domain]['extracted'], vpath.split('/', 1)[1] ])
        try:
            with open(path, 'rb') as file:
                root = xmlunpacker.read(file)
        except:
            root = None
    else:
        pkgpath = '/'.join([ config.BASE_DIR, config.PKG_RELPATH, config.DATA[domain]['packed'] ])
        try:
            with zipfile.ZipFile(pkgpath, 'r') as zip:
                with zip.open(vpath, 'r') as data:
                    root = xmlunpacker.read(io.BytesIO(data.read()))
        except:
            root = None
    return root


class Strage(object):

    def __init__(self):
        with open('itemdef.json', 'r') as fp:
            self.__itemdef = json.load(fp)
        self.__dictVehicle = {}
        self.__cacheVehicleInfo = {}
        self.__xmltree = {}
        
        self.__nationOrder = self.__fetchNationOrder()
        self.__vehicleList = self.__fetchVehicleList()

    def __find(self, resource, param):
        file = resource['file'].format(**param)
        xpath = resource['xpath'].format(**param)
        if file not in self.__xmltree:
            domain, target = file.split('/', 1)
            self.__xmltree[file] = readXmlData(domain, target)
        root = self.__xmltree[file]
        value = root.find(xpath)
        return value

    def find(self, category, node, param):
        result = None
        schema = self.__itemdef[category][node]
        for r in schema['resources']:
            result = self.__find(r, param)
            if result is not None:
                break
        if result is None:
            print('not found')
            return None
        if 'value' in schema:
            if schema['value'] == 'nodename':
                result = result.tag
            elif schema['value'] == 'nodelist':
                pass
        else:
            result = result.text
        if 'map' in schema:
            match = re.match('\[(\d)\]', str(schema['map']))
            if  schema['map'] == 'gettext':
                result = translate(result)
            elif isinstance(schema['map'], dict):
                values = result.split()
                result = [ schema['map'][v] for v in values if v in schema['map'] ]
                result = result.pop(0) if result else None
            elif match:
                result = result.split()[int(match.group(1))]
                print('match: ' + match.group(1))
        return result

    def __fetchNationOrder(self):
        root = readXmlData(config.GUI_SETTINGS)
        if root is None:
            return NATIONS
        for child in root:
            if child.tag == 'setting' and child.findtext('name') == 'nations_order':
                return [ i.text for i in child.find('value') ]

    def searchVehicle(self, vehicle):
        v = self.__dictVehicle[vehicle]
        return v['nation'], v['tag']

    def __fetchVehicleList(self):
        nations = self.__nationOrder
        tiers = TIERS
        types = TYPES_LIST
        vehicles = {}
        for nation in nations:
            vehicles[nation] = {}
            for tier in tiers:
                vehicles[nation][tier] = {}
                for type in types:
                    vehicles[nation][tier][type] = []
        for nation in nations:
            param = { 'nation': nation }
            items = [ node.tag for node in self.find('vehicle', 'list', param) ]
            for item in items:
                param = { 'nation': nation, 'vehicle': item }
                id = int(self.find('vehicle', 'id', param))
                tier = self.find('vehicle', 'tier', param)
                type = self.find('vehicle', 'type', param)
                secret = self.find('vehicle', 'secret', param)
                if not secret == 'secret' or config.secret:
                    vehicles[nation][tier][type].append({ 'id':id, 'vehicle':item })
        for nation, tier, type in product(nations, tiers, types):
            list = sorted(vehicles[nation][tier][type], key=lambda v: v['id'])
            vehicles[nation][tier][type] = [ v['vehicle'] for v in list ]
        return vehicles

    def fetchVehicleList(self, nation, tier, type):
        nations = [ n[0] for n in self.__nationOrder ] if nation == '*' else [ nation ]
        tiers = TIERS if tier == '*' else [ tier ]
        types = TYPES_LIST if type == '*' else [ type ]
        result = []
        for nation in nations:
            for tier, type in product(tiers, types):
                for vehicle in self.__vehicleList[nation][tier][type]:
                    param = { 'nation': nation, 'vehicle': vehicle }
                    userString = self.find('vehicle', 'userString', param)
                    shortUserString = self.find('vehicle', 'shortUserString', param)
                    result.append([ vehicle, shortUserString or userString ])
        return result

    def fetchNationList(self):
        return [ [ s, s.upper() ] for s in self.__nationOrder ]

    def fetchTierList(self):
        return [ [ tier, TIERS_LABEL[tier] ] for tier in TIERS ]

    def fetchTypeList(self):
        return [ [ type, type ] for type in TYPES_LIST ]

    def getDescription(self, category, param):
        schema = self.__itemdef['title'][category]
        values = [ self.find(category, name, param) for name in schema['value'] ]
        result = schema['format'].format(*values)
        return result

    def _getDropdownItems(self, category, items, param):
        result = []
        for item in items:
            param[category] = item
            result.append([ item, self.find(category, 'userString', param) ])
        return result

    def fetchChassisList(self, nation, vehicle):
        param = { 'nation': nation, 'vehicle': vehicle }
        items = [ node.tag for node in self.find('vehicle', 'chassis', param) ]
        return self._getDropdownItems('chassis', items, param)

    def fetchTurretList(self, nation, vehicle):
        param = { 'nation': nation, 'vehicle': vehicle }
        items = [ node.tag for node in self.find('vehicle', 'turrets', param) ]
        return self._getDropdownItems('turret', items, param)

    def fetchGunList(self, nation, vehicle, turret):
        param = { 'nation': nation, 'vehicle': vehicle, 'turret': turret }
        items = [ node.tag for node in self.find('turret', 'guns', param) ]
        return self._getDropdownItems('gun', items, param)

    def fetchShellList(self, nation, gun):
        param = { 'nation': nation, 'gun': gun }
        items = [ node.tag for node in self.find('gun', 'shots', param) ]
        return self._getDropdownItems('shell', items, param)


class Command:

    @staticmethod
    def listVehicle(strage, pattern):
        nation, tier, type = pattern.split(':')
        for r in strage.fetchVehicleList(nation.lower(), tier, type.upper()):
            print('{0[2]:<10}:{0[3]:<3}:{0[4]:<4}: {0[0]:<32}: {0[1]}'.format(r))

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
        nation, v = strage.searchVehicle(vehicle)
        for r in strage.fetchChassisList(nation, vehicle):
            print('{0[0]:<32}: {0[1]}'.format(r))

    @staticmethod
    def listTurret(strage, vehicle):
        nation, v = strage.searchVehicle(vehicle)
        for r in strage.fetchTurretList(nation, vehicle):
            print('{0[0]:<32}: {0[1]}'.format(r))

    @staticmethod
    def listGun(strage, vehicle, turret):
        nation, v = strage.searchVehicle(vehicle)
        for r in strage.fetchGunList(nation, vehicle, turret):
            print('{0[0]:<32}: {0[1]}'.format(r))

    @staticmethod
    def listShell(strage, nation, gun):
        for r in strage.fetchShellList(nation, gun):
            print('{0[0]:<32}: {0[1]}'.format(r))

    @staticmethod
    def infoVehicle(strage, vehicle):
        nation, v = strage.searchVehicle(vehicle)
        for k,v in strage.fetchVehicleInfo(nation, vehicle).items():
            print('{0:>32}: {1}'.format(k, v))

    @staticmethod
    def infoChassis(strage, vehicle, chassis):
        nation, v = strage.searchVehicle(vehicle)
        for k,v in strage.fetchChassisInfo(nation, vehicle, chassis).items():
            print('{0:>32}: {1}'.format(k, v))

    @staticmethod
    def infoTurret(strage, vehicle, turret):
        nation, v = strage.searchVehicle(vehicle)
        for k,v in strage.fetchTurretInfo(nation, vehicle, turret).items():
            print('{0:>32}: {1}'.format(k, v))

    @staticmethod
    def infoGun(strage, vehicle, turret, gun):
        nation, v = strage.searchVehicle(vehicle)
        for k,v in strage.fetchGunInfo(nation, vehicle, turret, gun).items():
            print('{0:>32}: {1}'.format(k, v))

    @staticmethod
    def infoShell(strage, nation, gun, shell):
        for k,v in strage.fetchShellInfo(nation, gun, shell).items():
            print('{0:>32}: {1}'.format(k, v))

    @staticmethod
    def infoVehicleFull(strage, vehicle, chassis, turret, gun, shell):
        nation, v = strage.searchVehicle(vehicle)
        for k,v in strage.fetchVehicleMergedInfo(nation, vehicle, chassis, turret, gun).items():
            print('{0:>32}: {1}'.format(k, v))
        import csvoutput
        print(csvoutput.createMessage(strage, nation, vehicle, chassis, turret, gun, shell))


def parseArgument():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='BASE_DIR', help='specify <WoT_game_folder>')
    parser.add_argument('-s', dest='SCRIPTS_DIR', help='scripts folder extracted.  ex. "C:\git\wot.scripts\scripts"')
    parser.add_argument('--secret', action='store_true', help='include secret tanks')
    
    if __name__ == '__main__':
        parser.add_argument('--list', dest='pattern', help='show vehicle list for NATION:TIER:TYPE.  ex. "germany:9:HT"')
        parser.add_argument('--list-nation', action='store_true', help='show nations')
        parser.add_argument('--list-tier', action='store_true', help='show tiers')
        parser.add_argument('--list-type', action='store_true', help='show vehicle types')
        parser.add_argument('--list-chassis', dest='vehicle_chassis', help='list chassis for vehicle.  ex. "R80_KV1"')
        parser.add_argument('--list-turret', dest='vehicle_turret', help='list turret for vehicle.  ex. "R80_KV1"')
        parser.add_argument('--list-gun', dest='vehicle_gun', help='list gun for vehicle and turret.  ex. "R80_KV1:Turret_2_KV1"')
        parser.add_argument('--list-shell', dest='gun_shell', help='list shell for gun and turret.  ex. "ussr:_85mm_F-30"')

        parser.add_argument('--info', dest='vehicle', help='view vehicle info')
        parser.add_argument('--info-chassis', dest='info_chassis', help='view chassis info for vehicle.  ex. "R80_KV1:Chassis_KV1_2"')
        parser.add_argument('--info-turret', dest='info_turret', help='view turret info for vehicle.  ex. "R80_KV1:Turret_2_KV1"')
        parser.add_argument('--info-gun', dest='info_gun', help='view gun info for vehicle.  ex. "R80_KV1:Turret_2_KV1:_85mm_F-30"')
        parser.add_argument('--info-shell', dest='info_shell', help='view for shell.  ex. "ussr:_85mm_F-30:_85mm_UBR-365K"')

        parser.add_argument('--info-full', dest='info_full', help='full view for vehicle.  ex. "R80_KV1:Chassis_KV1_2:Turret_2_KV1:_85mm_F-30:_85mm_UBR-365K"')

    parser.parse_args(namespace=config)
    if config.SCRIPTS_DIR:
        config.DATA[config.VEHICLES]['extracted'] = config.SCRIPTS_DIR


if __name__ == '__main__':
    import io, sys
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    parseArgument()
    strage = Strage()

    if config.list_nation:
        Command.listNation(strage)
    if config.list_tier:
        Command.listTier(strage)
    if config.list_type:
        Command.listType(strage)
    if config.pattern:
        Command.listVehicle(strage, config.pattern)
    if config.vehicle:
        Command.infoVehicle(strage, config.vehicle)
    if config.vehicle_chassis:
        Command.listChassis(strage, config.vehicle_chassis)
    if config.vehicle_turret:
        Command.listTurret(strage, config.vehicle_turret)
    if config.vehicle_gun:
        Command.listGun(strage, *config.vehicle_gun.split(':'))
    if config.gun_shell:
        Command.listShell(strage, *config.gun_shell.split(':'))

    if config.info_chassis:
        Command.infoChassis(strage, *config.info_chassis.split(':'))
    if config.info_turret:
        Command.infoTurret(strage, *config.info_turret.split(':'))
    if config.info_gun:
        Command.infoGun(strage, *config.info_gun.split(':'))
    if config.info_shell:
        Command.infoShell(strage, *config.info_shell.split(':'))

    if config.info_full:
        Command.infoVehicleFull(strage, *config.info_full.split(':'))
