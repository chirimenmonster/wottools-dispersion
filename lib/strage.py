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
        
        self.find = FindEntry().find
        
        self.__nationOrder = self.__fetchNationOrder()
        self.__vehicleList, self.__vehicleNation = self.__fetchVehicleList()

        self.__getDropdownList = {
            'nation':   self.fetchNationList,
            'tier':     self.fetchTierList,
            'type':     self.fetchTypeList,
            'vehicle':  self.fetchVehicleList,
            'chassis':  self.fetchChassisList,
            'turret':   self.fetchTurretList,
            'engine':   self.fetchEngineList,
            'radio':    self.fetchRadioList,
            'gun':      self.fetchGunList,
            'shell':    self.fetchShellList,
            'siege':    self.fetchSiegeList
        }

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


    def __getDropdownItems(self, category, items, param, schema=None):
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
        return self.__getDropdownItems('vehicle', items, param, schema=schema)

    def fetchChassisList(self, schema, param):
        if param['vehicle'] is None:
            return None
        items = [ node.tag for node in self.find('vehicle:chassis', param) ]
        return self.__getDropdownItems('chassis', items, param, schema=schema)

    def fetchTurretList(self, schema, param):
        if param['vehicle'] is None:
            return None
        items = [ node.tag for node in self.find('vehicle:turrets', param) ]
        return self.__getDropdownItems('turret', items, param, schema=schema)

    def fetchEngineList(self, schema, param):
        if param['vehicle'] is None:
            return None
        items = [ node.tag for node in self.find('vehicle:engines', param) ]
        return self.__getDropdownItems('engine', items, param, schema=schema)

    def fetchRadioList(self, schema, param):
        if param['vehicle'] is None:
            return None
        items = [ node.tag for node in self.find('vehicle:radios', param) ]
        return self.__getDropdownItems('radio', items, param, schema=schema)

    def fetchGunList(self, schema, param):
        if param['turret'] is None:
            return None
        items = [ node.tag for node in self.find('turret:guns', param) ]
        return self.__getDropdownItems('gun', items, param, schema=schema)

    def fetchShellList(self, schema, param):
        if param['gun'] is None:
            return None
        items = [ node.tag for node in self.find('gun:shots', param) ]
        return self.__getDropdownItems('shell', items, param, schema=schema)

    def fetchSiegeList(self, schema, param):
        if self.find('vehicle:siegeMode', param):
            result = [ [ None, 'normal' ], [ 'siege', 'siege' ] ]
        else:
            result = []
        return result


class FindEntry(object):

    def __init__(self):
        self.__itemschema = g_resources.itemschema
        self.__xmltree = {}
        self.__functions = {
            'sum':  self.__functionSum,
            'or':   self.__functionOr
        }

    def find(self, node, param):
        result = None
        schema = self.__itemschema[node]
        param = self.__getModifiedParam(node, param)
        result = None
        for r in schema['resources']:
            result = self.__getRawData(r, param)
            if result is not None:
                break
        if result is None:
            return None
        result = self.__convertType(schema, result)
        if 'map' in schema:
            result = self.__getMappedData(schema['map'], result)
        return result

    def __findNode(self, resource, param):
        fileparam = param.copy()
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

    def __getModifiedParam(self, node, param):
        schema = self.__itemschema[node]
        param = param.copy()
        if param.get('siege', None) == 'siege':
            if not node == 'vehicle:siegeMode' and self.find('vehicle:siegeMode', param):
                param['vehicle_file'] = param['vehicle'] + '_siege_mode'
        if 'addparams' in schema:
            for p in schema['addparams']:
                value = self.find(p['value'], param)
                param[p['xtag']] = value
        return param

    def __getRawData(self, resource, param):
        result = None
        if 'file' in resource:
            result = self.__findNode(resource, param)
        elif 'func' in resource:
            if resource['func'] in self.__functions:
                result = self.__functions[resource['func']](resource['args'], param)
            else:
                raise ValueError('unknown resource function: {}'.format(resource['func']))
        else:
            raise ValueError('missing valid resource: {}'.format(resource))
        return result

    def __convertType(self, schema, data):
        result = None
        if 'value' in schema:
            if schema['value'] == 'nodename':
                result = data.tag
            elif schema['value'] == 'nodelist':
                result = data
            elif schema['value'] == 'float':
                result = float(data.text)
            else:
                print('unknown value keyword: {}'.format(schema['value']))
                raise ValueError
        else:
            if isinstance(data, ElementTree.Element):
                result = data.text
            else:
                result = data
        return result

    def __getMappedData(self, map, data):
        if map == 'gettext':
            data = translate(data)
        elif map == 'roman':
            data = TIERS_LABEL[data]
        elif isinstance(map, dict):
            data = [ map[v] for v in data.split() if v in map ]
            data = data.pop(0) if data else None
        else:
            match = re.match('\[(\d)\]', str(map))
            if match:
                data = data.split()[int(match.group(1))]
            else:
                raise ValueError('unknown map method: {}'.map)
        return data
        
    def __functionSum(self, args, param):
        result = 0
        for arg in args:
            value = float(self.find(arg, param))
            result += value
        return result
            
    def __functionOr(self, args, param):
        result = None
        for arg in args:
            result = self.find(arg, param)
            if result:
                break
        return result

