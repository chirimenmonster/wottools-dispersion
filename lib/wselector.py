
from collections import namedtuple
import tkinter.ttk

from lib.query import VehicleSpec, ModuleSpec


SelectorItem = namedtuple('SelectorItem', 'id name')


class SelectorPanel(tkinter.Frame):

    def __init__(self, *args, app=None, desc=None, **kwargs):
        super(SelectorPanel, self).__init__(*args, **kwargs, borderwidth=0, padx=4)
        self.app = app
        label = Label(self, **desc['option']['label'])
        label.pack(side='left')
        selector = SelectorFactory().create(desc['id'], master=self, app=app, **desc['option']['combobox'])
        selector.pack(side='left')
        selector.preferredLast = desc.get('selected', 'first') == 'last'
        self.app.widgets[selector.winfo_name()] = selector
        self.selector = selector

    def setup(self):
        self.selector.setup()


class Label(tkinter.Label):
    pass


class SelectorFactory(object):
    def create(self, name, *args, **kwargs):
        table = {
            'nation':   NationSelector,
            'tier':     TierSelector,
            'type':     VTypeSelector,
            'vehicle':  VehicleSelector,
            'secret':   SecretSelector,
            'siege':    SiegeSelector,
            'chassis':  ChassisSelector,
            'turret':   TurretSelector,
            'engine':   EngineSelector,
            'radio':    RadioSelector,
            'gun':      GunSelector,
            'shell':    ShellSelector
        }
        return table[name](*args, **kwargs)


class Selector(tkinter.ttk.Combobox):

    def __init__(self, *args, app=None, **kwargs):
        super(Selector, self).__init__(*args, **kwargs)
        self['state'] = 'disable'
        self.app = app
        self.__table = None
        self.preferredLast = False
        self.onSelected = []
        self.bind('<<ComboboxSelected>>', self.processOnSelected)

    def setup(self):
        self.updateTable()

    def processOnSelected(self, event):
        for handler in self.onSelected:
            handler()

    def updateTable(self):
        pass

    def setTable(self, table):
        self.__table = table
        if table is None or len(table) == 0:
            self['value'] = [ '' ]
            self.current(0)
            self['state'] = 'disable'
        else:
            self['values'] = list(map(lambda x: x.name, table))
            index = len(table) - 1 if self.preferredLast else 0 
            self.current(index)
            self['state'] = 'readonly'
        self.processOnSelected(None)

    def getId(self):
        if 'disabled' in self.state():
            return None
        index = self.current()
        id = self.__table[index].id
        return id


class NationSelector(Selector):
    def updateTable(self):
        nationsOrder = self.app.resource.getValue('settings:nationsOrder')
        table = [ SelectorItem(nation, nation.upper()) for nation in nationsOrder ]
        self.setTable(table)

class TierSelector(Selector):
    def __init__(self, *args, **kwargs):
        super(TierSelector, self).__init__(*args, **kwargs, justify='center')

    def updateTable(self):
        tiersOrder = self.app.resource.getValue('settings:tiersOrder')
        tiersLabel = self.app.resource.getValue('settings:tiersLabel')
        table = [ SelectorItem(tier, tiersLabel[tier]) for tier in map(str, tiersOrder) ]
        self.setTable(table)

class VTypeSelector(Selector):
    def __init__(self, *args, **kwargs):
        super(VTypeSelector, self).__init__(*args, **kwargs, justify='center')

    def updateTable(self):
        typesOrder = self.app.resource.getValue('settings:typesOrder')
        table = [ SelectorItem(vtype, vtype) for vtype in typesOrder ]
        self.setTable(table)


class SecretSelector(Selector):
    table = [ SelectorItem(flag, flag) for flag in ('False', 'True') ]

    def updateTable(self):
        self.setTable(self.table)


class VehicleSelector(Selector):
    def setup(self, *args, **kwargs):
        super(VehicleSelector, self).setup(*args, **kwargs)
        self.app.widgets['!nationselector'].onSelected.append(self.updateTable)
        self.app.widgets['!tierselector'].onSelected.append(self.updateTable)
        self.app.widgets['!vtypeselector'].onSelected.append(self.updateTable)
        self.app.widgets['!secretselector'].onSelected.append(self.updateTable)

    def updateTable(self):
        nation = self.app.widgets['!nationselector'].getId()
        tier = self.app.widgets['!tierselector'].getId()
        vtype = self.app.widgets['!vtypeselector'].getId()
        secret = self.app.widgets['!secretselector'].getId()
        nations = [nation]
        vtypes = [vtype]
        tiers = [int(tier)]
        secrets = { 'True':[True, False], 'False':[False] }.get(secret, None)
        ctxs = self.app.vd.getVehicleCtx(VehicleSpec(nations, tiers, vtypes, secrets))
        tags = ('vehicle:index', 'vehicle:userString')
        table = [ SelectorItem(*self.app.vd.getVehicleItems(tags, c).values()) for c in ctxs ]
        self.setTable(table)


class SiegeSelector(Selector):

    table = [
        SelectorItem('', ''),
        SelectorItem('siegeMode', 'siege')
    ]    

    def setup(self, *args, **kwargs):
        super(SiegeSelector, self).setup(*args, **kwargs)
        self.app.widgets['!vehicleselector'].onSelected.append(self.updateTable)

    def updateTable(self):
        vehicle = self.app.widgets['!vehicleselector'].getId()
        if vehicle is None:
            self.setTable(None)
            return
        ctx = self.app.vd.getCtx(vehicle)
        items = self.app.vd.getVehicleItems(['vehicle:siegeMode'], ctx)
        if items['vehicle:siegeMode'] != 'siegeMode':
            self.setTable(None)
            return
        self.setTable(self.table)


class ModuleSelector(Selector):
    modulename = None
    moduletags = None

    def setup(self, *args, **kwargs):
        super(ModuleSelector, self).setup(*args, **kwargs)
        self.app.widgets['!vehicleselector'].onSelected.append(self.updateTable)

    def updateTable(self):
        vehicle = self.app.widgets['!vehicleselector'].getId()
        if vehicle is None:
            self.setTable(None)
            return
        ctx = self.app.vd.getCtx(vehicle)
        ctx.update(self.requiredModules())
        moduleids = self.app.vd.getModuleList(self.modulename, ctx)
        table = []
        for mid in moduleids:
            ctx[self.modulename] = mid
            items = self.app.vd.getVehicleItems(self.moduletags, ctx)
            table.append(SelectorItem(*[ items[k] for k in self.moduletags ]))
        self.setTable(table)

    def requiredModules(self):
        return {}


class ChassisSelector(ModuleSelector):
    modulename = 'chassis'
    moduletags = ('chassis:index', 'chassis:userString')

class TurretSelector(ModuleSelector):
    modulename = 'turret'
    moduletags = ('turret:index', 'turret:userString')

class EngineSelector(ModuleSelector):
    modulename = 'engine'
    moduletags = ('engine:index', 'engine:userString')

class RadioSelector(ModuleSelector):
    modulename = 'radio'
    moduletags = ('radio:index', 'radio:userString')


class GunSelector(ModuleSelector):
    modulename = 'gun'
    moduletags = ('gun:index', 'gun:userString')

    def setup(self, *args, **kwargs):
        super(GunSelector, self).setup(*args, **kwargs)
        self.app.widgets['!turretselector'].onSelected.append(self.updateTable)

    def requiredModules(self):
        turret = self.app.widgets['!turretselector'].getId()
        return { 'turret':turret }


class ShellSelector(ModuleSelector):
    modulename = 'shell'
    moduletags = ('shell:index', 'shell:displayString')

    def setup(self, *args, **kwargs):
        super(ShellSelector, self).setup(*args, **kwargs)
        self.app.widgets['!gunselector'].onSelected.append(self.updateTable)

    def requiredModules(self):
        turret = self.app.widgets['!turretselector'].getId()
        gun = self.app.widgets['!gunselector'].getId()
        return { 'turret':turret, 'gun':gun }
