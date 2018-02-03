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
    return None

def getEntryTextSafe(e):
    if e is not None:
        return e.text
    return ''


class Strage(object):

    def __init__(self):
        self.__strage = {}
        self.__strageSharedGun = {}
        root = readPackedXml(configs.GUISETTINGS_VPATH, package=configs.GUI_RELPATH)
        for child in root:
            if child.tag == 'setting' and child.find('name') is not None and child.find('name').text == 'nations_order':
                self.__nations = [ i.text for i in child.find('value') ]
                break
        for nation in self.__nations:
            root = readPackedXml(configs.BASEREL_DIR + '/' + nation + '/list.xml')
            for child in root:
                entry = {}
                id = nation + '/' + child.tag
                entry['id'] = id
                entry['tag'] = child.tag
                entry['nation'] = nation
                entry['tier'] = child.find('level').text
                entry['order'] = int(child.find('id').text)
                entry['type'] = [ TYPES_LABEL[t] for t in child.find('tags').text.split(' ') if t in TYPES ][0]
                entry['userString'] = child.find('userString').text
                entry['name'] = translate(entry['userString'])
                self.__strage[id] = entry
            root = readPackedXml(configs.BASEREL_DIR + '/' + nation + '/components/guns.xml')
            for gun in root.find('shared'):
                entry = {}
                id = nation + '/' + gun.tag
                entry['id'] = id
                entry['tag'] = gun.tag
                entry['nation'] = nation
                entry['userString'] = gun.find('userString').text
                entry['shotDispersionRadius'] = gun.find('shotDispersionRadius').text
                shotDispersionFactors = gun.find('shotDispersionFactors')
                entry['turretRotation'] = shotDispersionFactors.find('turretRotation').text
                entry['afterShot'] = shotDispersionFactors.find('afterShot').text
                entry['whileGunDamaged'] = shotDispersionFactors.find('whileGunDamaged').text
                self.__strageSharedGun[id] = entry

    def getSharedGunEntry(self, entry, target, nation, gunTag, label):
        if entry is not None:
            result = entry.find(target)
            if result is not None:
                return result.text
        id = nation + '/' + gunTag
        return self.__strageSharedGun[id][label]
                
    def fetchVehicleInfo(self, id):
        nation, tag = id.split('/')
        root = readPackedXml(configs.BASEREL_DIR + '/' + nation + '/' + tag + '.xml')
        entry = { k:v for k,v in self.__strage[id].items() }
        entry['chassis'] = {}
        entry['chassisList'] = []
        for chassis in root.find('chassis'):
            desc = {}
            desc['tag'] = chassis.tag
            desc['userString'] = chassis.find('userString').text
            desc['name'] = translate(desc['userString'])
            shotDispersionFactors = chassis.find('shotDispersionFactors')
            desc['vehicleMovement'] = shotDispersionFactors.find('vehicleMovement').text
            desc['vehicleRotation'] = shotDispersionFactors.find('vehicleRotation').text
            entry['chassis'][desc['tag']] = desc
            entry['chassisList'].append(desc['tag'])
        entry['turret'] = {}
        entry['turretList'] = []
        entry['gun'] = {}
        entry['gunList'] = []
        for turret in root.find('turrets0'):
            desc = {}
            desc['tag'] = turret.tag
            desc['userString'] = turret.find('userString').text
            desc['name'] = translate(desc['userString'])
            desc['gun'] = {}
            desc['gunList'] = []
            entry['turret'][desc['tag']] = desc
            entry['turretList'].append(desc['tag'])
            for gun in turret.find('guns'):
                gunDesc = {}
                gunDesc['tag'] = gun.tag
                gunDesc['userString'] = self.getSharedGunEntry(gun, 'userString', nation, gun.tag, 'userString')
                gunDesc['name'] = translate(gunDesc['userString'])
                gunDesc['shotDispersionRadius'] = self.getSharedGunEntry(gun, 'shotDispersionRadius', nation, gun.tag, 'shotDispersionRadius')
                shotDispersionFactors = gun.find('shotDispersionFactors')
                gunDesc['turretRotation'] = self.getSharedGunEntry(shotDispersionFactors, 'turretRotation', nation, gun.tag, 'turretRotation')
                gunDesc['afterShot'] = self.getSharedGunEntry(shotDispersionFactors, 'afterShot', nation, gun.tag, 'afterShot')
                gunDesc['whileGunDamaged'] = self.getSharedGunEntry(shotDispersionFactors, 'whileGunDamaged', nation, gun.tag, 'whileGunDamaged')
                desc['gun'][gunDesc['tag']] = gunDesc
                desc['gunList'].append(gunDesc['tag'])
        return entry

    def fetchChassisInfo(self, vid, tag):
        chassis = self.fetchVehicleInfo(vid)['chassis']
        return chassis[tag]

    def fetchTurretInfo(self, vid, tag):
        turret = self.fetchVehicleInfo(vid)['turret']
        return turret[tag]

    def fetchGunInfo(self, vid, tid, tag):
        gun = self.fetchVehicleInfo(vid)['turret'][tid]['gun']
        return gun[tag]
        
    def fetchNationList(self):
        return [ s.upper() for s in self.__nations ], self.__nations

    def fetchTierList(self):
        return TIERS, TIERS

    def fetchTypeList(self):
        return TYPES_LIST, TYPES_LIST

    def fetchVehicleList(self, nation, tier, type):
        list = [ v for v in self.__strage.values() if v['nation'] == nation and v['tier'] == tier and v['type'] == type ]
        list = sorted(list, key=lambda x: x['order'])
        return [ v['name'] for v in list ], [ v['id'] for v in list ]

    def fetchChassisList(self, vid):
        vehicleInfo = self.fetchVehicleInfo(vid)
        labels = [ 'chassis: ' + vehicleInfo['chassis'][tag]['name'] for tag in vehicleInfo['chassisList'] ]
        return [ labels, vehicleInfo['chassisList'] ]

    def fetchTurretList(self, vid):
        vehicleInfo = self.fetchVehicleInfo(vid)
        labels = [ 'turret: ' + vehicleInfo['turret'][tag]['name'] for tag in vehicleInfo['turretList'] ]
        return [ labels, vehicleInfo['turretList'] ]

    def fetchGunList(self, vid, tid):
        vehicleInfo = self.fetchVehicleInfo(vid)
        gunList = vehicleInfo['turret'][tid]['gunList']
        labels = [ 'gun: ' + vehicleInfo['turret'][tid]['gun'][tag]['name'] for tag in gunList ]
        return [ labels, vehicleInfo['turret'][tid]['gunList'] ]

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

    print(g_strage.fetchGunList('germany/G25_PzII_Luchs', 'PzIIL_Grosseturm'))
    #print(g_strage.fetchVehicleList('germany', '7', 'TD'))
    #print(g_strage.fetchVehicleInfo('germany/G18_JagdPanther'))
    #print(g_strage.fetchVehicleInfo('germany/G110_Typ_205'))
