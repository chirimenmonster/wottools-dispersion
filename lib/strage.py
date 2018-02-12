import re
from itertools import product
from xml.etree import ElementTree

from lib.config import g_config as config
from lib.resources import g_resources, NATIONS, TIERS, TIERS_LABEL, TYPES
from lib.translate import g_translate as translate
from lib.utils import readXmlData

class Strage(object):

    def __init__(self):
        self.__itemschema = g_resources.itemschema
        self.__titlesdesc = g_resources.titlesdesc
        self.__itemgroup = g_resources.itemgroup
        self.__dictVehicle = {}
        self.__cacheVehicleInfo = {}
        self.__xmltree = {}
        
        self.__nationOrder = self.__fetchNationOrder()
        self.__vehicleList, self.__vehicleNation = self.__fetchVehicleList()

        func = {}
        func['nation'] = self.fetchNationList
        func['tier'] = self.fetchTierList
        func['type'] = self.fetchTypeList
        func['vehicle'] = self.fetchVehicleList
        func['chassis'] = self.fetchChassisList
        func['turret'] = self.fetchTurretList
        func['engine'] = self.fetchEngineList
        func['radio'] = self.fetchRadioList
        func['gun'] = self.fetchGunList
        func['shell'] = self.fetchShellList
        func['siege'] = self.fetchSiegeList
        self.__getDropdownList = func

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
        types = TYPES
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

    def getDescription(self, param):
        values = []
        for schema in self.__titlesdesc:
            value = []
            for item in schema['value']:
                value.append(self.find(item, param))
            values.append([ schema['label'], *value ])
        values.append([ 'Siege:', param['siege'] or 'None' ])
        for column in self.__itemgroup:
            for row in column:
                for schema in row['items']:
                    value = self.find(schema['value'], param)
                    values.append([ schema['label'], value, schema.get('unit', ''), schema['value'] ])
        return values

    def getVehicleInfo(self, param):
        items = []
        for column in self.__itemgroup:
            for row in column:
                items += row['items']
        result = []
        for target in items:
            result.append([ node, strage.find(target, param) ])
        return result

    def getDropdownList(self, schema, param):
        return self.__getDropdownList[schema['id']](schema, param)
 
    def fetchNationList(self, schema, param):
        return [ [ s, s.upper() ] for s in self.__nationOrder ]

    def fetchTierList(self, schema, param):
        return [ [ tier, TIERS_LABEL[tier] ] for tier in TIERS ]

    def fetchTypeList(self, schema, param):
        return [ [ type, type ] for type in TYPES ]


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
        types = TYPES if param['type'] == '*' else [ param['type'] ]
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
        if param['gun'] is None:
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
