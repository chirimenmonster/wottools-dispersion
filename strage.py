import gettext
from xml.etree import ElementTree

class Configs:
    pass

configs = Configs()
configs.BASEDIR = 'C:/Games/World_of_Tanks'
configs.PKG_RELPATH = 'res/packages/scripts.pkg'
configs.GUI_RELPATH = 'res/packages/gui.pkg'
configs.BASEREL_DIR = 'scripts/item_defs/vehicles'
configs.LOCALE_RELPATH = 'res'
configs.GUISETTINGS_VPATH = 'gui/gui_settings.xml'

TIERS = [ str(tier) for tier in range(1, 10 + 1) ]
TIERS_LABEL = { '1':'I', '2':'II', '3':'III', '4':'IV', '5':'V', '6':'VI', '7':'VII', '8':'VIII', '9':'IX', '10':'X'}
TIERS_LIST = [ TIERS_LABEL[t] for t in TIERS ]

TYPES = [ 'lightTank', 'mediumTank', 'heavyTank', 'AT-SPG', 'SPG' ]
TYPES_LABEL = { 'lightTank':'LT', 'mediumTank':'MT', 'heavyTank':'HT', 'AT-SPG':'TD', 'SPG':'SPG' }
TYPES_LIST = [ TYPES_LABEL[t] for t in TYPES ]

_currentDomain = None
_translation = None

def translate(text):
    global _currentDomain
    global _translation
    if not text[0] == '#':
        return text
    prefix, name = text.split(':')
    if not _currentDomain == prefix.replace('#', ''):
        _currentDomain = prefix.replace('#', '')
        localedir = configs.BASEDIR + '/' + configs.LOCALE_RELPATH
        _translation = gettext.translation(_currentDomain, languages=['text'], localedir=localedir)
        _translation.install()
    name2 = _(name)
    return name2


def readPackedXml(relPath, package=None):
    import io
    import zipfile
    from XmlUnpacker import XmlUnpacker
    xmlunpacker = XmlUnpacker()
    root = None
    if not package:
        pkgPath = configs.BASEDIR + '/' + configs.PKG_RELPATH
    else:
        pkgPath = configs.BASEDIR + '/' + package
    with zipfile.ZipFile(pkgPath, 'r') as zip:
        with zip.open(relPath, 'r') as file:
            root = xmlunpacker.read(io.BytesIO(file.read()))
    return root


def getEntityTextSafe(entity, default):
    if entity is not None:
        return entity.text
    return default


class Strage(object):

    def __init__(self):
        self.__strageVehicleList = {}
        self.__strageSharedGuns = {}
        self.__cacheVehicleInfo = {}
        self.__nationOrder = self.__fetchNationOrder()
        for nation in self.__nationOrder:
            self.__strageVehicleList[nation] = StrageVehicleList(nation)
            self.__strageSharedGuns[nation] = StrageSharedGuns(nation)

    def __fetchNationOrder(self):
        root = readPackedXml(configs.GUISETTINGS_VPATH, package=configs.GUI_RELPATH)
        for child in root:
            if child.tag == 'setting' and child.find('name') is not None and child.find('name').text == 'nations_order':
                return [ i.text for i in child.find('value') ]

    def getVehicleEntry(self, nation, vehicle):
        return self.__strageVehicleList[nation].getEntry(vehicle)

    def getSharedGunEntry(self, nation, gun):
        return self.__strageSharedGuns[nation].getEntry(gun)

    def fetchVehicleInfo(self, nation, vehicle):
        if vehicle not in self.__cacheVehicleInfo:
            self.__cacheVehicleInfo[vehicle] = StrageVehicle(nation, vehicle)
        return self.__cacheVehicleInfo[vehicle]

    def fetchChassisInfo(self, nation, vehicle, chassis):
        vehicleInfo = self.fetchVehicleInfo(nation, vehicle)
        return vehicleInfo.fetchChassisInfo(chassis)

    def fetchTurretInfo(self, nation, vehicle, turret):
        vehicleInfo = self.fetchVehicleInfo(nation, vehicle)
        return vehicleInfo.fetchTurretInfo(turret)

    def fetchGunInfo(self, nation, vehicle, turret, gun):
        vehicleInfo = self.fetchVehicleInfo(nation, vehicle)
        return vehicleInfo.fetchGunInfo(turret, gun)

    def fetchVehicleList(self, nation, tier, type):
        list = [ v for v in self.__strageVehicleList[nation].getStrage().values() if v['tier'] == tier and v['type'] == type ]
        list = sorted(list, key=lambda x: x['id'])
        return [ v['shortUserString'] or v['name'] for v in list ], [ v['tag'] for v in list ]

    def fetchNationList(self):
        return [ [ s, s.upper() ] for s in self.__nationOrder ]

    def fetchTierList(self):
        return [ [ tier, TIERS_LABEL[tier] ] for tier in TIERS_LIST ]

    def fetchTypeList(self):
        return [ [ type, type ] for type in TYPES_LIST ]

    def fetchChassisList(self, nation, vehicle):
        vehicleInfo = self.fetchVehicleInfo(nation, vehicle)
        return vehicleInfo.fetchChassisList()

    def fetchTurretList(self, nation, vehicle):
        vehicleInfo = self.fetchVehicleInfo(nation, vehicle)
        return vehicleInfo.fetchTurretList()

    def fetchGunList(self, nation, vehicle, turret):
        vehicleInfo = self.fetchVehicleInfo(nation, vehicle)
        gunList = vehicleInfo.fetchGunList(turret)
        return gunList


class StrageVehicleList(object):

    def __init__(self, nation):
        root = readPackedXml(configs.BASEREL_DIR + '/' + nation + '/list.xml')
        self.__strage = {}
        for vehicle in root:
            entry = {}
            entry['id'] = int(vehicle.find('id').text)
            entry['tag'] = vehicle.tag
            entry['nation'] = nation
            entry['tier'] = vehicle.find('level').text
            entry['type'] = [ TYPES_LABEL[t] for t in vehicle.find('tags').text.split(' ') if t in TYPES ][0]
            entry['userString'] = vehicle.find('userString').text
            entry['name'] = translate(entry['userString'])
            shortUserString = vehicle.find('shortUserString')
            if shortUserString:
                entry['shortUserString'] = translate(shortUserString.text)
            else:
                entry['shortUserString'] = ''
            entry['description'] = translate(vehicle.find('description').text)
            self.__strage[vehicle.tag] = entry

    def getEntry(self, tag):
        return self.__strage[tag]

    def getStrage(self):
        return self.__strage


class StrageSharedGuns(object):
    __strage = {}

    def __init__(self, nation):
        root = readPackedXml(configs.BASEREL_DIR + '/' + nation + '/components/guns.xml')
        for gun in root.find('ids'):
            entry = {}
            entry['id'] = int(gun.text)
            entry['tag'] = gun.tag
            entry['nation'] = nation
            self.__strage[gun.tag] = entry
        for gun in root.find('shared'):
            entry = self.__fetchGunEntry(gun)
            for k,v in entry.items():
                self.__strage[gun.tag][k] = v

    def __fetchGunEntry(self, gun):
        entry = {}
        entry['userString'] = gun.find('userString').text
        entry['reloadTime'] = gun.find('reloadTime').text
        entry['aimingTime'] = gun.find('aimingTime').text
        entry['shotDispersionRadius'] = gun.find('shotDispersionRadius').text
        factors = gun.find('shotDispersionFactors')
        entry['turretRotation'] = factors.find('turretRotation').text
        entry['afterShot'] = factors.find('afterShot').text
        entry['whileGunDamaged'] = factors.find('whileGunDamaged').text
        return entry
    
    def getEntry(self, tag):
        return self.__strage[tag]


class StrageVehicle(object):

    def __init__(self, nation, vehicle):
        self.__currentNation = nation
        root = readPackedXml(configs.BASEREL_DIR + '/' + nation + '/' + vehicle + '.xml')
        
        entry = self.__fetchVehicleEntry(root, vehicle)
        self.__vehicle = entry
        
        self.__chassis = {}
        self.__chassisList = []
        for chassis in root.find('chassis'):
            entry = self.__fetchChassisEntry(chassis, chassis.tag)
            self.__chassis[chassis.tag] = entry
            self.__chassisList.append(chassis.tag)
        
        self.__turret = {}
        self.__turretList = []
        for turret in root.find('turrets0'):
            entry = self.__fetchTurretEntry(turret, turret.tag)
            self.__turret[turret.tag] = entry
            self.__turretList.append(turret.tag)

        self.__gun = {}
        self.__gunList = {}
        for turret in root.find('turrets0'):
            self.__gun[turret.tag] = {}
            self.__gunList[turret.tag] = []
            for gun in turret.find('guns'):
                entry = self.__fetchGunEntry(gun, gun.tag)
                self.__gun[turret.tag][gun.tag] = entry
                self.__gunList[turret.tag].append(gun.tag)

    def __fetchVehicleEntry(self, tree, vehicle):
        shared = g_strage.getVehicleEntry(self.__currentNation, vehicle)
        entry = { k:v for k,v in shared.items() }
        return entry

    def __fetchChassisEntry(self, tree, chassis):
        entry = {}
        entry['tag'] = chassis
        entry['userString'] = tree.find('userString').text
        entry['name'] = translate(entry['userString'])
        factors = tree.find('shotDispersionFactors')
        entry['vehicleMovement'] = factors.find('vehicleMovement').text
        entry['vehicleRotation'] = factors.find('vehicleRotation').text
        return entry

    def __fetchTurretEntry(self, tree, turret):
        entry = {}
        entry['tag'] = turret
        entry['userString'] = tree.find('userString').text
        entry['name'] = translate(entry['userString'])
        return entry

    def __fetchGunEntry(self, tree, gun):
        shared = g_strage.getSharedGunEntry(self.__currentNation, gun)
        entry = {}
        entry['tag'] = gun
        entry['userString'] = getEntityTextSafe(tree.find('userString'), shared['userString'])
        entry['name'] = translate(entry['userString'])
        entry['reloadTime'] = getEntityTextSafe(tree.find('reloadTime'), shared['reloadTime'])
        entry['aimingTime'] = getEntityTextSafe(tree.find('aimingTime'), shared['aimingTime'])
        entry['shotDispersionRadius'] = getEntityTextSafe(tree.find('shotDispersionRadius'), shared['shotDispersionRadius'])
        factors = tree.find('shotDispersionFactors')
        if factors is not None:
            entry['turretRotation'] = getEntityTextSafe(factors.find('turretRotation'), shared['turretRotation'])
            entry['afterShot'] = getEntityTextSafe(factors.find('afterShot'), shared['afterShot'])
            entry['whileGunDamaged'] = getEntityTextSafe(factors.find('whileGunDamaged'), shared['whileGunDamaged'])
        else:
            for k in [ 'turretRotation', 'afterShot', 'whileGunDamaged' ]:
                entry[k] = shared[k]
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

    def fetchTurretList(self):
        return [ [ tag, self.__turret[tag]['name'] ] for tag in self.__turretList ]
        
    def fetchGunList(self, turret):
        return [ [ tag, self.__gun[turret][tag]['name'] ] for tag in self.__gunList[turret] ]



if __name__ == '__main__':
    import io, sys
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='BASEDIR', help='specify <WoT_game_folder>')
    parser.parse_args(namespace=configs)

    g_strage = Strage()

    print(configs.BASEDIR)
    
    print(g_strage.fetchVehicleList('germany', '7', 'TD'))
    print(g_strage.fetchVehicleInfo('germany', 'G110_Typ_205'))
    #print(g_strage.fetchVehicleInfo('germany', 'G18_JagdPanther'))
    print(g_strage.fetchGunList('germany', 'G25_PzII_Luchs', 'PzIIL_Grosseturm'))
    #print(g_strage.fetchVehicleInfo('germany/G18_JagdPanther'))
