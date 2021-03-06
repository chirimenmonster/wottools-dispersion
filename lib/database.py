
from collections import namedtuple

VehicleTag = namedtuple('VehicleTag', 'nation id vehicle tier type secret', defaults=(None, None, None, None, None, None))
VehicleSpec = namedtuple('VehicleSpec', 'nations tiers types secrets', defaults=(None, None, None, None))
ModuleSpec = namedtuple('ModuleSpec', 'chassis turret engine radio gun shell', defaults=(-1, -1, -1, -1, -1, 0))
MODULE_SELECTABLE = [ 'chassis', 'turret', 'engine', 'radio', 'gun', 'shell' ]


class VehicleDatabase(object):

    def setup(self, resource):
        self.resource = resource
        nationsOrder = self.resource.getValue('settings:nationsOrder')
        tiers = self.resource.getValue('settings:tiersOrder')
        types = self.resource.getValue('settings:typesOrder')
        vehicles = []
        for nation in nationsOrder:
            ctx = {'nation':nation}
            result = self.resource.getValue('vehicle:list', ctx)
            vehicles.extend([ {'nation':nation, 'vehicle':v} for v in result ])
        self.__keys = []
        self.__indexes = {}
        for ctx in vehicles:
            ctx['id'] = int(self.resource.getValue('vehicle:id', ctx))
            ctx['tier'] = int(self.resource.getValue('vehicle:tier', ctx))
            ctx['type'] = self.resource.getValue('vehicle:type', ctx)
            ctx['secret'] = True if self.resource.getValue('vehicle:secret', ctx) == 'secret' else False
            tag = VehicleTag(**ctx)
            self.__keys.append(tag)
            self.__indexes[tag.vehicle] = tag

    def getCtx(self, vehicle):
        #result = self.__indexes.get(vehicle, VehicleTag())
        result = self.__indexes.get(vehicle, None)
        if result is None:
            return None
        return result._asdict()

    def getVehicleCtx(self, vehicleSpec=None):
        if isinstance(vehicleSpec, list):
            result = [ self.getCtx(v) for v in vehicleSpec ]
            result = list(filter(lambda x: x is not None, result))
            return result
        if vehicleSpec is None:
            vehicleSpec = VehicleSpec()
        nations, tiers, types, secrets = vehicleSpec
        def dynfilter(x):
            if nations and x.nation not in nations:
                return False
            if tiers and x.tier not in tiers:
                return False
            if types and x.type not in types:
                return False
            if (secrets is None and x.secret) or (secrets and x.secret not in secrets):
                return False
            return True
        result = list(map(lambda x:x._asdict(), filter(dynfilter, self.__keys)))
        return result

    def getModuleList(self, module, ctx):
        tag = {
            'chassis':  'vehicle:chassis',
            'turret':   'vehicle:turrets',
            'engine':   'vehicle:engines',
            'radio':    'vehicle:radios',
            'gun':      'turret:guns',
            'shell':    'gun:shots'
        }[module]
        result = self.resource.getValue(tag, ctx)
        return result

    def getVehicleItems(self, tags, ctx):
        ctx = ctx.copy()
        if ctx.get('siege', None) == 'siegeMode':
            ctx['vehicle_siege'] = ctx['vehicle'] + '_siege_mode'
        else:
            ctx['vehicle_siege'] = ctx['vehicle']
        result = {}
        for tag in tags:
            value = self.resource.getRefValue(tag, ctx)
            result[tag] = value
        return result

    def getModuleCtx(self, vehicle, moduleSpec=None):
        ctx = self.getCtx(vehicle)
        if ctx is None:
            return []
        ctxs = [ ctx ]
        for module in MODULE_SELECTABLE:
            attr = getattr(moduleSpec, module) if moduleSpec is not None else None
            if attr is None:
                index = None
                name = None
            elif isinstance(attr, int):
                index = attr
                name = None
            elif isinstance(attr, str):
                index = None
                name = attr
            else:
                raise ValueError('bad module specified: {}, {}, {}'.format(module, attr, moduleSpec))
            newctxlist = []
            for ctx in ctxs:
                moduleList = self.getModuleList(module, ctx)
                if index is not None:
                    try:
                        moduleList = [ moduleList[index] ]
                    except IndexError as e:
                        raise IndexError('{}, moduleList={}, index={}'.format(e.args, moduleList, index))
                elif name is not None:
                    if name in moduleList:
                        moduleList = [ name ]
                    else:
                        moduleList = []
                for moduleID in moduleList:
                    newctx = ctx.copy()
                    newctx[module] = moduleID
                    newctxlist.append(newctx)
            ctxs = newctxlist
        return ctxs

    def getVehicleModuleCtx(self, vehicleSpec=None, moduleSpec=None):
        ctxs = []
        for ctx in self.getVehicleCtx(vehicleSpec):
            vehicle = ctx['vehicle']
            ctxs.extend(self.getModuleCtx(vehicle, moduleSpec))
        return ctxs
