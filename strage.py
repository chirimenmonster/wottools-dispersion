from itertools import product
import re
import json
from xml.etree import ElementTree

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
        with open('itemschema.json', 'r') as fp:
            self.__itemschema = json.load(fp)
        with open('guisettings_items.json', 'r') as fp:
            self.__itemgroup = json.load(fp)
        self.__dictVehicle = {}
        self.__cacheVehicleInfo = {}
        self.__xmltree = {}
        
        self.__nationOrder = self.__fetchNationOrder()
        self.__vehicleList, self.__vehicleNation = self.__fetchVehicleList()

    def __find(self, resource, param):
        fileparam = { k:v for k,v in param.items() }
        if 'vehicle_file' in fileparam:
            fileparam['vehicle'] = fileparam['vehicle_file']
        file = resource['file'].format(**fileparam)
        xpath = resource['xpath'].format(**param)
        if file not in self.__xmltree:
            domain, target = file.split('/', 1)
            self.__xmltree[file] = readXmlData(domain, target)
        root = self.__xmltree[file]
        if root is None:
            print('cannot read file {}'.format(file))
        value = root.find(xpath)
        return value

    def findfunc_sum(self, args, param):
        result = 0
        for arg in args:
            value = float(self.find(arg, param))
            result += value
        return result
            
    def findfunc_or(self, args, param):
        result = None
        for arg in args:
            result = self.find(arg, param)
            if result:
                break
        return result

    def find(self, node, param):
        result = None
        schema = self.__itemschema[node]
        param = { k:v for k,v in param.items() }
        if param.get('siege', None) == 'siege':
            if not node == 'vehicle:siegeMode' and self.find('vehicle:siegeMode', param):
                param['vehicle_file'] = param['vehicle'] + '_siege_mode'
        if 'addparams' in schema:
            for p in schema['addparams']:
                value = self.find(p['value'], param)
                param[p['xtag']] = value
        for r in schema['resources']:
            if 'file' in r:
                result = self.__find(r, param)
            elif 'func' in r:
                if r['func'] == 'sum':
                    result = self.findfunc_sum(r['args'], param)
                elif r['func'] == 'or':
                    result = self.findfunc_or(r['args'], param)
                else:
                    raise ValueError('unknown resource function: {}'.format(r['func']))
            else:
                raise ValueError('missing valid resources: {}'.format(r))
            if result is not None:
                break
        if result is None:
            return None
        if 'value' in schema:
            if schema['value'] == 'nodename':
                result = result.tag
            elif schema['value'] == 'nodelist':
                pass
            elif schema['value'] == 'function':
                pass
            elif schema['value'] == 'float':
                result = float(result.text)
            else:
                raise ValueError('unknown value keyword: {}'.schema['value'])
        else:
            if isinstance(result, ElementTree.Element):
                result = result.text
        if 'map' in schema:
            match = re.match('\[(\d)\]', str(schema['map']))
            if match:
                result = result.split()[int(match.group(1))]
            elif isinstance(schema['map'], dict):
                values = result.split()
                result = [ schema['map'][v] for v in values if v in schema['map'] ]
                result = result.pop(0) if result else None
            elif schema['map'] == 'gettext':
                result = translate(result)
            elif schema['map'] == 'roman':
                result = TIERS_LABEL[result]
            else:
                raise ValueError('unknown map method: {}'.schema['map'])
        return result

    def __fetchNationOrder(self):
        root = readXmlData(config.GUI_SETTINGS)
        if root is None:
            return NATIONS
        for child in root:
            if child.tag == 'setting' and child.findtext('name') == 'nations_order':
                return [ i.text for i in child.find('value') ]

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
            items = [ node.tag for node in self.find('vehicle:list', param) ]
            for item in items:
                param = { 'nation': nation, 'vehicle': item }
                id = int(self.find('vehicle:id', param))
                tier = self.find('vehicle:tier', param)
                type = self.find('vehicle:type', param)
                secret = self.find('vehicle:secret', param)
                if not secret == 'secret' or config.secret:
                    vehicles[nation][tier][type].append({ 'id':id, 'vehicle':item })
        rev = {}
        for nation, tier, type in product(nations, tiers, types):
            list = sorted(vehicles[nation][tier][type], key=lambda v: v['id'])
            vehicles[nation][tier][type] = [ v['vehicle'] for v in list ]
            for v in list:
                rev[v['vehicle']] = nation
        return vehicles, rev

    def getVehicleNation(self, vehicle):
        return self.__vehicleNation[vehicle]

    def getVehicleDescription(self, param):
        result = []
        for node in [ 'vehicle', 'chassis', 'turret', 'engine', 'radio', 'gun', 'shell' ]:
            value = self.getDescription(node, param)
            result.append([ node, self.__itemdef['title'][node]['format'].format(*value) ])
        return result

    def getVehicleInfo(self, param):
        items = []
        for column in self.__itemgroup:
            for row in column:
                items += row['items']
        result = []
        for target in items:
            result.append([ node, strage.find(target, param) ])
        return result

    def fetchNationList(self, schema, param):
        return [ [ s, s.upper() ] for s in self.__nationOrder ]

    def fetchTierList(self, schema, param):
        return [ [ tier, TIERS_LABEL[tier] ] for tier in TIERS ]

    def fetchTypeList(self, schema, param):
        return [ [ type, type ] for type in TYPES_LIST ]


    def _getDropdownItems(self, category, items, param, schema=None):
        result = []
        param = param.copy()
        for item in items:
            param[category] = item
            if schema and schema.get('label', None):
                format = schema['label']['format']
                values = [ self.find(node, param) for node in schema['label']['value'] ]
                text = format.format(*values)
            else:
                text = self.find(category + ':userString', param)
            result.append([ item, text ])
        return result

    def fetchVehicleList(self, schema, param):
        nations = [ n[0] for n in self.__nationOrder ] if param['nation'] == '*' else [ param['nation'] ]
        tiers = TIERS if param['tier'] == '*' else [ param['tier'] ]
        types = TYPES_LIST if param['type'] == '*' else [ param['type'] ]
        items = []
        for nation, tier, type in product(nations, tiers, types):
            items.extend(self.__vehicleList[nation][tier][type])
        return self._getDropdownItems('vehicle', items, param, schema=schema)

    def fetchChassisList(self, schema, param):
        if param['vehicle'] is None:
            return None
        items = [ node.tag for node in self.find('vehicle:chassis', param) ]
        return self._getDropdownItems('chassis', items, param, schema=schema)

    def fetchTurretList(self, schema, param):
        if param['vehicle'] is None:
            return None
        items = [ node.tag for node in self.find('vehicle:turrets', param) ]
        return self._getDropdownItems('turret', items, param, schema=schema)

    def fetchEngineList(self, schema, param):
        if param['vehicle'] is None:
            return None
        items = [ node.tag for node in self.find('vehicle:engines', param) ]
        return self._getDropdownItems('engine', items, param, schema=schema)

    def fetchRadioList(self, schema, param):
        if param['vehicle'] is None:
            return None
        items = [ node.tag for node in self.find('vehicle:radios', param) ]
        return self._getDropdownItems('radio', items, param, schema=schema)

    def fetchGunList(self, schema, param):
        if param['vehicle'] is None:
            return None
        items = [ node.tag for node in self.find('turret:guns', param) ]
        return self._getDropdownItems('gun', items, param, schema=schema)

    def fetchShellList(self, schema, param):
        if param['vehicle'] is None:
            return None
        items = [ node.tag for node in self.find('gun:shots', param) ]
        return self._getDropdownItems('shell', items, param, schema=schema)

    def fetchSiegeList(self, schema, param):
        if param['vehicle'] is None:
            return None
        if self.find('vehicle:siegeMode', param):
            result = [
                [ None, 'normal' ],
                [ 'siege', 'siege' ]
            ]
        else:
            result = []
        return result

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
        parser.add_argument('--list-engine', dest='vehicle_engine', help='list engine for vehicle.  ex. "R80_KV1"')
        parser.add_argument('--list-radio', dest='vehicle_radio', help='list radio for vehicle.  ex. "R80_KV1"')
        parser.add_argument('--list-gun', dest='vehicle_gun', help='list gun for vehicle and turret.  ex. "R80_KV1:Turret_2_KV1"')
        parser.add_argument('--list-shell', dest='gun_shell', help='list shell for gun and turret.  ex. "ussr:_85mm_F-30"')

        parser.add_argument('--info', dest='vehicle', help='view info for vehicle.  ex. "R80_KV1:Chassis_KV1_2:Turret_2_KV1:V-2K:_10RK:_85mm_F-30:_85mm_UBR-365K"')

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
