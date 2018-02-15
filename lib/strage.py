from itertools import product

from lib.config import g_config as config
from lib.resources import g_resources, NATIONS, TIERS, TIERS_LABEL, TYPES
from lib.translate import g_translate as translate
from lib.item import FindFormattedEntry

class Strage(object):

    def __init__(self):
        self.__itemschema = g_resources.itemschema
        self.__titlesdesc = g_resources.titlesdesc
        self.__itemgroup = g_resources.itemgroup
        
        self.__findEntry = FindFormattedEntry()
        self.find = self.__findEntry.find
        self.findText = self.__findEntry.getText
        
        self.__nationOrder = self.find('settings:nationsOrder', {})
        print(self.__nationOrder)
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
        return self.__getDropdownList[schema['id']](schema.get('label', None), param)
 
    def fetchNationList(self, schema, param):
        return [ [ s, s.upper() ] for s in self.__nationOrder ]

    def fetchTierList(self, schema, param):
        return [ [ tier, TIERS_LABEL[tier] ] for tier in TIERS ]

    def fetchTypeList(self, schema, param):
        return [ [ type, type ] for type in TYPES ]


    def __getDropdownItems(self, category, items, param, schema):
        param = param.copy()
        if schema is None:
            schema = { 'value': category + ':userString' }
        result = []
        for item in items:
            param[category] = item
            text = self.findText(schema, param)
            result.append([ item, text ])
        return result

    def fetchVehicleList(self, schema, param):
        nations = [ n[0] for n in self.__nationOrder ] if param['nation'] == '*' else [ param['nation'] ]
        tiers = TIERS if param['tier'] == '*' else [ param['tier'] ]
        types = TYPES if param['type'] == '*' else [ param['type'] ]
        items = []
        for nation, tier, type in product(nations, tiers, types):
            items.extend(self.__vehicleList[nation][tier][type])
        return self.__getDropdownItems('vehicle', items, param, schema)

    def fetchChassisList(self, schema, param):
        nodes = self.find('vehicle:chassis', param)
        items = [ node.tag for node in nodes ] if nodes else []
        return self.__getDropdownItems('chassis', items, param, schema)

    def fetchTurretList(self, schema, param):
        nodes = self.find('vehicle:turrets', param)
        items = [ node.tag for node in nodes ] if nodes else []
        return self.__getDropdownItems('turret', items, param, schema)

    def fetchEngineList(self, schema, param):
        nodes = self.find('vehicle:engines', param)
        items = [ node.tag for node in nodes ] if nodes else []
        return self.__getDropdownItems('engine', items, param, schema)

    def fetchRadioList(self, schema, param):
        nodes = self.find('vehicle:radios', param)
        items = [ node.tag for node in nodes ] if nodes else []
        return self.__getDropdownItems('radio', items, param, schema)

    def fetchGunList(self, schema, param):
        nodes = self.find('turret:guns', param)
        items = [ node.tag for node in nodes ] if nodes else []
        return self.__getDropdownItems('gun', items, param, schema)

    def fetchShellList(self, schema, param):
        nodes = self.find('gun:shots', param)
        items = [ node.tag for node in nodes ] if nodes else []
        return self.__getDropdownItems('shell', items, param, schema)

    def fetchSiegeList(self, schema, param):
        value = self.find('vehicle:siegeMode', param)
        result = [ [ None, 'normal' ], [ 'siege', 'siege' ] ] if value else []
        return result