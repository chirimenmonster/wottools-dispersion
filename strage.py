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
        self.__strageVehicleList = {}
        self.__strageSharedGuns = {}
        self.__strageSharedShells = {}
        self.__dictVehicle = {}
        self.__cacheVehicleInfo = {}
        self.__xmltree = {}
        self.__nationOrder = self.__fetchNationOrder()
        for nation in self.__nationOrder:
            vehicleList = StrageVehicleList(nation)
            sharedGuns = StrageSharedGuns(nation)
            sharedShells = StrageSharedShells(nation)

            self.__strageVehicleList[nation] = vehicleList
            self.__strageSharedGuns[nation] = sharedGuns
            self.__strageSharedShells[nation] = sharedShells
            
            for k,v in self.__strageVehicleList[nation].getStrage().items():
                self.__dictVehicle[k] = v

    def __findtext(self, resource, param):
        print('*', resource, param, flush=True)
        file = resource['file'].format(**param)
        xpath = resource['xpath'].format(**param)
        print('*', file, xpath, flush=True)
        if file not in self.__xmltree:
            domain, target = file.split('/', 1)
            self.__xmltree[file] = readXmlData(domain, target)
        root = self.__xmltree[file]
        print('*', file, xpath, param, flush=True)
        value = root.findtext(xpath)
        if 'type' in resource and resource['type'] == 'array':
            values = value.split()
            if 'index' in resource:
                value = values[resource['index']]
            elif 'match' in resource:
                result = [ resource['match'][v] for v in values if v in resource['match'] ]
                value = result.pop(0) if result else None
                print(value, flush=True)
        return value

    def findtext(self, category, node, param):
        for r in self.__itemdef[category][node]['resources']:
            print(r, flush=True)
            result = self.__findtext(r, param)
            if result is not None:
                return result
        return None

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
        for r in self.__itemdef[category][node]['resources']:
            result = self.__find(r, param)
            if result is not None:
                return result
        return None

    def __fetchNationOrder(self):
        root = readXmlData(config.GUI_SETTINGS)
        if root is None:
            return NATIONS
        for child in root:
            if child.tag == 'setting' and child.findtext('name') == 'nations_order':
                return [ i.text for i in child.find('value') ]

    def getVehicleEntry(self, nation, vehicle):
        return self.__strageVehicleList[nation].getEntry(vehicle)

    def getSharedGunEntry(self, nation, gun):
        return self.__strageSharedGuns[nation].getEntry(gun)

    def searchVehicle(self, vehicle):
        v = self.__dictVehicle[vehicle]
        return v['nation'], v['tag']

    def __fetchVehicleInfo(self, nation, vehicle):
        if vehicle not in self.__cacheVehicleInfo:
            strage = StrageVehicle(nation, vehicle, self)
            self.__cacheVehicleInfo[vehicle] = strage
            self.__xmltree[strage.filename] = strage.root
        return self.__cacheVehicleInfo[vehicle]

    def fetchVehicleInfo(self, nation, vehicle):
        vehicleInfo = self.__fetchVehicleInfo(nation, vehicle)
        return vehicleInfo.fetchVehicleInfo()

    def fetchChassisInfo(self, nation, vehicle, chassis):
        vehicleInfo = self.__fetchVehicleInfo(nation, vehicle)
        return vehicleInfo.fetchChassisInfo(chassis)

    def fetchTurretInfo(self, nation, vehicle, turret):
        vehicleInfo = self.__fetchVehicleInfo(nation, vehicle)
        return vehicleInfo.fetchTurretInfo(turret)

    def fetchGunInfo(self, nation, vehicle, turret, gun):
        vehicleInfo = self.__fetchVehicleInfo(nation, vehicle)
        return vehicleInfo.fetchGunInfo(turret, gun)

    def fetchVehicleMergedInfo(self, nation, vehicle, chassis, turret, gun):
        _vehicle = self.__fetchVehicleInfo(nation, vehicle)
        vehicleInfo = _vehicle.fetchVehicleInfo()
        chassisInfo = _vehicle.fetchChassisInfo(chassis)
        turretInfo = _vehicle.fetchTurretInfo(turret)
        gunInfo = _vehicle.fetchGunInfo(turret, gun)
        result = {}
        result = { k:v for k,v in vehicleInfo.items() }
        result.update({ 'chassis:'+k:v for k,v in chassisInfo.items() })
        result.update({ 'turret:'+k:v for k,v in turretInfo.items() })
        result.update({ 'gun:'+k:v for k,v in gunInfo.items() })
        return result

    def fetchShellInfo(self, nation, gun, shell):
        result = {}
        result.update(self.__strageSharedShells[nation].getEntry(shell))
        result.update(self.__strageSharedGuns[nation].getShotEntry(gun, shell))
        return result

    def fetchVehicleList(self, nation, tier, type):
        nations = [ n[0] for n in self.fetchNationList() ] if nation == '*' else [ nation ]
        tiers = TIERS if tier == '*' else [ tier ]
        types = TYPES_LIST if type == '*' else [ type ]
        nation_order = { v:i for i,v in enumerate(nations) }
        type_order = { v:i for i,v in enumerate(types) }
        vehicles = []
        for nation in nations:
            vehicles.extend(self.__strageVehicleList[nation].getStrage().values())
        vehicles = [ v for v in vehicles if v['tier'] in tiers and v['type'] in types ]
        if not config.secret:
            vehicles = [ v for v in vehicles if not v['secret'] ]
        vehicles = sorted(vehicles, key=lambda v: (int(v['tier']), type_order[v['type']], nation_order[v['nation']], v['id']))
        result = [ [ v['tag'], v['shortUserString'] or v['name'], v['nation'], v['tier'], v['type'] ] for v in vehicles ]
        return result

    def fetchNationList(self):
        return [ [ s, s.upper() ] for s in self.__nationOrder ]

    def fetchTierList(self):
        return [ [ tier, TIERS_LABEL[tier] ] for tier in TIERS ]

    def fetchTypeList(self):
        return [ [ type, type ] for type in TYPES_LIST ]

    def fetchChassisList(self, nation, vehicle):
        vehicleInfo = self.__fetchVehicleInfo(nation, vehicle)
        return vehicleInfo.fetchChassisList()

    def fetchTurretList(self, nation, vehicle):
        param = { 'nation': nation, 'vehicle': vehicle }
        result = self.find('vehicle', 'turrets', param)
        turrets = [ node.tag for node in result ]
        result = []
        for turret in turrets:
            param['turret'] = turret
            print(param, flush=True)
            result.append([ turret, self.findtext('turret', 'userString', param) ])
        print(result, flush=True)
        return result

    def fetchGunList(self, nation, vehicle, turret):
        param = { 'nation': nation, 'vehicle': vehicle, 'turret': turret }
        result = self.find('turret', 'guns', param)
        guns = [ node.tag for node in result ]
        result = []
        for gun in guns:
            param['gun'] = gun
            print(param, flush=True)
            result.append([ gun, self.findtext('gun', 'userString', param) ])
        print(result, flush=True)
        return result

    def fetchShellList(self, nation, gun):
        param = { 'nation': nation, 'gun': gun }
        result = self.find('gun', 'shots', param)
        shells = [ node.tag for node in result ]
        result = []
        for shell in shells:
            param['shell'] = shell
            result.append([ shell, self.findtext('shell', 'userString', param) ])
        print(result, flush=True)
        return result


class StrageVehicleList(object):

    def __init__(self, nation):
        self.filename = '/'.join([ config.VEHICLES, nation, 'list.xml' ])
        self.root = readXmlData(config.VEHICLES, '/'.join([ nation, 'list.xml' ]))
        self.__strage = {}
        for vehicle in self.root:
            entry = {}
            entry['id'] = int(vehicle.findtext('id'))
            entry['tag'] = vehicle.tag
            entry['nation'] = nation
            entry['tier'] = vehicle.findtext('level')
            entry['userString'] = vehicle.findtext('userString')
            entry['name'] = translate(entry['userString'])
            entry['shortUserString'] = translate(vehicle.findtext('shortUserString'))
            entry['description'] = translate(vehicle.findtext('description'))
            entry['attr'] = vehicle.findtext('tags').split()
            entry['secret'] = False
            for attr in entry['attr']:
                if attr in TYPES:
                    entry['type'] = TYPES_LABEL[attr]
                elif attr in 'secret':
                    entry['secret'] = True
            self.__strage[vehicle.tag] = entry

    def getEntry(self, tag):
        return self.__strage[tag]

    def getStrage(self):
        return self.__strage


class StrageSharedGuns(object):

    def __init__(self, nation):
        self.filename = '/'.join([ config.VEHICLES, nation, 'components/guns.xml' ])
        self.root = readXmlData(config.VEHICLES, '/'.join([ nation, 'components/guns.xml' ]))
        self.__gun = {}
        for gun in self.root.find('ids'):
            entry = {}
            entry['id'] = int(gun.text)
            entry['tag'] = gun.tag
            entry['nation'] = nation
            self.__gun[gun.tag] = entry
        for gun in self.root.find('shared'):
            entry = self.__fetchGunEntry(gun)
            for k,v in entry.items():
                self.__gun[gun.tag][k] = v
        self.__shot = {}
        self.__shotList = {}
        for gun in self.root.find('shared'):
            self.__shot[gun.tag] = {}
            self.__shotList[gun.tag] = []
            for shot in gun.find('shots'):
                entry = self.__fetchShotEntry(shot, gun.tag, shot.tag)
                self.__shot[gun.tag][shot.tag] = entry
                self.__shotList[gun.tag].append(shot.tag)            

    def __fetchGunEntry(self, gun):
        entry = {}
        entry['userString'] = gun.findtext('userString')
        entry['name'] = translate(entry['userString'])
        return entry

    def __fetchShotEntry(self, tree, gun, shot):
        entry = {}
        entry['tag'] = shot
        return entry
        
    def getEntry(self, gun):
        return self.__gun[gun]

    def getShotEntry(self, gun, shell):
        return self.__shot[gun][shell]


class StrageSharedShells(object):

    def __init__(self, nation):
        self.filename = '/'.join([ config.VEHICLES, nation, 'components/shells.xml' ])
        self.root = readXmlData(config.VEHICLES, '/'.join([ nation, 'components/shells.xml' ]))
        self.__shell = {}
        for shell in self.root:
            if shell.find('id') is None:
                continue
            entry = {}
            entry['id'] = shell.findtext('id')
            entry['tag'] = shell.tag
            entry['userString'] = shell.findtext('userString')
            entry['name'] = translate(entry['userString'])
            self.__shell[shell.tag] = entry

    def getEntry(self, shell):
        return self.__shell[shell]


class StrageVehicle(object):

    def __init__(self, nation, vehicle, common):
        self.__common = common
        self.__currentNation = nation
        self.filename = '/'.join([ config.VEHICLES, nation, vehicle + '.xml' ])
        self.root = readXmlData(config.VEHICLES, '/'.join([ nation, vehicle + '.xml' ]))

        entry = self.__fetchVehicleEntry(self.root, vehicle)
        self.__vehicle = entry
        
        self.__chassis = {}
        self.__chassisList = []
        for chassis in self.root.find('chassis'):
            entry = self.__fetchChassisEntry(chassis, chassis.tag)
            self.__chassis[chassis.tag] = entry
            self.__chassisList.append(chassis.tag)
        
        self.__turret = {}
        self.__turretList = []
        for turret in self.root.find('turrets0'):
            entry = self.__fetchTurretEntry(turret, turret.tag)
            self.__turret[turret.tag] = entry
            self.__turretList.append(turret.tag)

        self.__gun = {}
        self.__gunList = {}
        for turret in self.root.find('turrets0'):
            self.__gun[turret.tag] = {}
            self.__gunList[turret.tag] = []
            for gun in turret.find('guns'):
                entry = self.__fetchGunEntry(gun, gun.tag)
                self.__gun[turret.tag][gun.tag] = entry
                self.__gunList[turret.tag].append(gun.tag)

    def __fetchVehicleEntry(self, tree, vehicle):
        shared = self.__common.getVehicleEntry(self.__currentNation, vehicle)
        entry = { k:v for k,v in shared.items() }
        return entry

    def __fetchChassisEntry(self, tree, chassis):
        entry = {}
        entry['tag'] = chassis
        entry['userString'] = tree.findtext('userString')
        entry['name'] = translate(entry['userString'])
        entry['attr'] = tree.findtext('tags').split()
        return entry

    def __fetchTurretEntry(self, tree, turret):
        entry = {}
        entry['tag'] = turret
        entry['userString'] = tree.findtext('userString')
        entry['name'] = translate(entry['userString'])
        entry['attr'] = tree.findtext('tags').split()
        return entry

    def __fetchGunEntry(self, tree, gun):
        shared = self.__common.getSharedGunEntry(self.__currentNation, gun)
        entry = {}
        entry['tag'] = gun
        entry['userString'] = tree.findtext('userString') or shared['userString']
        entry['name'] = translate(entry['userString'])
        return entry
 
    def fetchVehicleInfo(self):
        return self.__vehicle

    def fetchChassisInfo(self, chassis):
        return self.__chassis[chassis]

    def fetchTurretInfo(self, turret):
        return self.__turret[turret]

    def fetchGunInfo(self, turret, gun):
        return self.__gun[turret][gun]

    def fetchChassisList(self):
        return [ [ tag, self.__chassis[tag]['name'] ] for tag in self.__chassisList ]



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
