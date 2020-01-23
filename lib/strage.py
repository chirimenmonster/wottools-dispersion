from itertools import product

from lib.config import g_config as config
from lib.resources import g_resources, TIERS, TIERS_LABEL, TYPES
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
        self.__vehicleList = self.__fetchVehicleList()
        self.__vehicleIndex = self.__createIndexVehicle(self.__vehicleList)

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
            items = [ node.tag for node in self.find('vehicle:list', param) if node.tag != 'xmlns:xmlref' ]
            for item in items:
                param = { 'nation': nation, 'vehicle': item }
                id = int(self.find('vehicle:id', param))
                tier = self.find('vehicle:tier', param)
                type = self.find('vehicle:type', param)
                secret = self.find('vehicle:secret', param)
                data = { 'id':id, 'vehicle':item, 'nation':nation, 'tier':tier, 'type':type, 'secret':secret }
                if not secret == 'secret' or config.secret:
                    vehicles[nation][tier][type].append(data)
        for nation, tier, type in product(nations, tiers, types):
            list = sorted(vehicles[nation][tier][type], key=lambda v: v['id'])
            vehicles[nation][tier][type] = list
        return vehicles

    def __createIndexVehicle(self, database):
        index = {}
        for nation in database.keys():
            for tier in database[nation].keys():
                for type in database[nation][tier].keys():
                    for data in database[nation][tier][type]:
                        index[data['vehicle']] = data
        return index

    def getParamFromVehicle(self, vehicle):
        return self.__vehicleIndex[vehicle]

    def getVehicleNation(self, vehicle):
        return self.__vehicleIndex[vehicle]['nation']

    def getDescription(self, param):
        titles = self.getVehicleDescription(param)
        values = self.getVehicleInfo(param)
        return titles, values

    def getVehicleDescription(self, param):
        titles = []
        for schema in self.__titlesdesc:
            value = []
            for item in schema['value']:
                value.append(self.findText({ 'value':item }, param))
            titles.append([ schema['label'], *value ])
        titles.append([ 'Siege:', param['siege'] or 'None' ])
        return titles

    def getVehicleInfo(self, param):
        values = []
        for column in self.__itemgroup['columns']:
            for row in column['rows']:
                for schema in row['items']:
                    value = self.find(schema['value'], param)
                    header = [ schema['value'], schema['label'], schema.get('unit', '') ]
                    values.append(header + (value if isinstance(value, list) else [ value ]) )
        return values

    def getVehicleItemsInfo(self, vehicleSpec, tags):
        result = { t:self.find(t, vehicleSpec) for t in tags }
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
        nations = [ n for n in self.__nationOrder ] if param['nation'] == '*' else [ param['nation'] ]
        tiers = TIERS if param['tier'] == '*' else [ param['tier'] ]
        types = TYPES if param['type'] == '*' else [ param['type'] ]
        result = []
        for nation in nations:
            items = []
            for tier, type in product(tiers, types):
                items.extend([ v['vehicle'] for v in self.__vehicleList[nation][tier][type] ])
            newparam = param.copy()
            newparam['nation'] = nation
            result.extend(self.__getDropdownItems('vehicle', items, newparam, schema))
        return result

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



    def getVehicleItemsInfo(self, vspec, tags):
        result = {}
        for nodeId in tags:
            value = self.find(nodeId, vspec)
            result[nodeId] = value
        return result


    def getModuleList(self, vspec, module):
        id = {
            'chassis':  'vehicle:chassis',
            'turret':   'vehicle:turrets',
            'engine':   'vehicle:engines',
            'radio':    'vehicle:radios',
            'gun':      'turret:guns',
            'shell':    'gun:shots'
        }[module]
        nodes = self.find(id, vspec)
        tags = [ n.tag for n in nodes ] if nodes else []
        return tags


    def getVehicleList(self, vfilter):
        nations = self.__nationOrder
        tiers = TIERS
        types = TYPES
        if 'nation' in vfilter and isinstance(vfilter['nation'], list):
            for n in vfilter['nation']:
                if n not in self.__nationOrder:
                    raise ValueError('incorrect nation designation: "{}"'.format(vfilter['nation']))
            nation = vfilter['nation']
        if 'tier' in vfilter and isinstance(vfilter['tier'], list):
            for t in vfilter['tier']:
                if t not in TIERS:
                    raise ValueError('incorrect tier designation: "{}"'.format(vfilter['tier']))
            tiers = vfilter['tier']
        if 'type' in vfilter and isinstance(vfilter['type'], list):
            for vt in vfilter['type']:
                if vt not in TYPES:
                    raise ValueError('incorrect vehicle type designation: "{}"'.format(vfilter['type']))
            types = vfilter['type']
        vehicles = []
        for nation in nations:
            for tier in tiers:
                for vtype in types:
                    vehicles.extend(self.__vehicleList[nation][tier][vtype])
        result = [ d['vehicle'] for d in vehicles ]
        return result
