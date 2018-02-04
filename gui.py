import tkinter
import tkinter.ttk
import tkinter.font

from strage import Strage, configs

class Application(tkinter.Frame):

    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        self.font = tkinter.font.Font(family='Arial', size=11, weight='normal')
        self.option_add('*font', self.font)
        self.option_add('*background', 'white')
        self.option_add('*relief', 'flat')
        self.master.title('Vehicle Selector')
        self.master.config(background='white', relief='flat')
        self.createWidgets()

    def createWidgets(self):
        vehicleSelectorBar = tkinter.Frame(self.master)
        vehicleSelectorBar.pack(side='top', expand=1, fill='x', padx=4, pady=1)

        moduleSelectorBar = tkinter.Frame(self.master)
        moduleSelectorBar.pack(side='top', expand=1, fill='x', padx=4, pady=1)

        modulePanel = tkinter.Frame(self.master, highlightthickness=1, highlightbackground='gray')
        modulePanel.pack(side='top', expand=1, fill='x', padx=8, pady=4)

        itemPanel = tkinter.Frame(self.master, highlightthickness=1, highlightbackground='gray')
        itemPanel.pack(side='top', expand=1, fill='x', padx=8, pady=4)
        
        self.__nationSelector = DropdownList(vehicleSelectorBar, width=10, label='Nation')
        self.__nationSelector.pack(side='left')
        self.__nationSelector.setValues(*g_strage.fetchNationList())
        self.__nationSelector.setCallback(self.cbChangeVehicleFilter)

        self.__tierSelector = DropdownList(vehicleSelectorBar, width=3, label='Tier')
        self.__tierSelector.pack(side='left')
        self.__tierSelector.setValues(*g_strage.fetchTierList())
        self.__tierSelector.setCallback(self.cbChangeVehicleFilter)

        self.__typeSelector = DropdownList(vehicleSelectorBar, width=4, label='Type')
        self.__typeSelector.pack(side='left')
        self.__typeSelector.setValues(*g_strage.fetchTypeList())
        self.__typeSelector.setCallback(self.cbChangeVehicleFilter)

        self.__vehicleSelector = DropdownList(vehicleSelectorBar, width=60, label='Vehicle')
        self.__vehicleSelector.pack(side='left')
        self.__vehicleSelector.setCallback(self.cbChangeVehicle)

        self.__chassisSelector = DropdownList(moduleSelectorBar, width=32, label='Chassis')
        self.__chassisSelector.pack(side='left')
        self.__chassisSelector.setCallback(self.cbChangeModules)

        self.__turretSelector = DropdownList(moduleSelectorBar, width=32, label='Turret')
        self.__turretSelector.pack(side='left')
        self.__turretSelector.setCallback(self.cbChangeTurret)

        self.__gunSelector = DropdownList(moduleSelectorBar, width=32, label='Gun')
        self.__gunSelector.pack(side='left')
        self.__gunSelector.setCallback(self.cbChangeModules)

        self.__item = {}
        self.__item['vehicle'] = PanelItem(modulePanel, 'Vehicle:', '', labelWidth=8, valueWidth=60, valueAnchor='w')
        self.__item['chassis'] = PanelItem(modulePanel, 'Chassis:', '', labelWidth=8, valueWidth=60, valueAnchor='w')
        self.__item['turret'] = PanelItem(modulePanel, 'Turret:', '', labelWidth=8, valueWidth=60, valueAnchor='w')
        self.__item['gun'] = PanelItem(modulePanel, 'Gun:', '', labelWidth=8, valueWidth=60, valueAnchor='w')
        self.__item['reloadTime'] = PanelItem(itemPanel, 'reload time:', ' (s)')
        self.__item['aimingTime'] = PanelItem(itemPanel, 'aiming time:', ' (s)')
        self.__item['shotDispersionRadius'] = PanelItem(itemPanel, 'shot dispersion radius:', ' (m)')
        PanelItem(itemPanel, 'DispersionFactor', '', labelAnchor='w')
        self.__item['vehicleMovement'] = PanelItem(itemPanel, '... vehicle movement:', '')
        self.__item['vehicleRotation'] = PanelItem(itemPanel, '... vehicle rotation:', '')
        self.__item['turretRotation'] = PanelItem(itemPanel, '... turret rotation:', '')
        self.__item['afterShot'] = PanelItem(itemPanel, '... after shot:', '')
        self.__item['whileGunDamaged'] = PanelItem(itemPanel, '... while gun damaged:', '')

        self.changeVehicleFilter()
        self.changeVehicle()
        self.changeModules()

    def changeVehicleFilter(self):
        nation = self.__nationSelector.getSelected()
        tier = self.__tierSelector.getSelected()
        type = self.__typeSelector.getSelected()
        vehicles = g_strage.fetchVehicleList(nation, tier, type)
        if not vehicles[0]:
            vehicles = [ [ '' ], [ None ] ]
        self.__vehicleSelector.setValues(*vehicles)
        self.changeVehicle()

    def changeVehicle(self):
        vehicleId = self.__vehicleSelector.getSelected()
        if vehicleId:
            vehicleInfo = g_strage.fetchVehicleInfo(vehicleId)
            self.__chassisSelector.setValues(*g_strage.fetchChassisList(vehicleId))
            self.__turretSelector.setValues(*g_strage.fetchTurretList(vehicleId))
        else:
            self.__chassisSelector.setValues([ '' ], [ None ])
            self.__turretSelector.setValues([ '' ], [ None ])
        self.changeTurret()

    def changeTurret(self):
        vehicleId = self.__vehicleSelector.getSelected()
        if vehicleId:
            turretTag = self.__turretSelector.getSelected()
            self.__gunSelector.setValues(*g_strage.fetchGunList(vehicleId, turretTag))
        else:
            self.__gunSelector.setValues([ '' ], [ None ])
        self.changeModules()

    def changeModules(self):
        vehicleId = self.__vehicleSelector.getSelected()
        if vehicleId:
            vehicleInfo = g_strage.fetchVehicleInfo(vehicleId)
            self.__item['vehicle'].setValue('{} ({})'.format(vehicleInfo['name'], vehicleInfo['id']))
            chassisTag = self.__chassisSelector.getSelected()
            turretTag = self.__turretSelector.getSelected()
            gunTag = self.__gunSelector.getSelected()
            chassis = g_strage.fetchChassisInfo(vehicleId, chassisTag)
            turret = g_strage.fetchTurretInfo(vehicleId, turretTag)
            gun = g_strage.fetchGunInfo(vehicleId, turretTag, gunTag)
            self.__item['chassis'].setValue('{} ({})'.format(chassis['name'], chassis['tag']))
            self.__item['turret'].setValue('{} ({})'.format(turret['name'], turret['tag']))
            self.__item['gun'].setValue('{} ({})'.format(gun['name'], gun['tag']))
            self.__item['reloadTime'].setValue(gun['reloadTime'])
            self.__item['aimingTime'].setValue(gun['aimingTime'])
            self.__item['shotDispersionRadius'].setValue(gun['shotDispersionRadius'])
            self.__item['vehicleMovement'].setValue(chassis['vehicleMovement'])
            self.__item['vehicleRotation'].setValue(chassis['vehicleRotation'])
            self.__item['turretRotation'].setValue(gun['turretRotation'])
            self.__item['afterShot'].setValue(gun['afterShot'])
            self.__item['whileGunDamaged'].setValue(gun['whileGunDamaged'])
        else:
            for panel in self.__item.values():
                panel.setValue('')

    def cbChangeVehicleFilter(self, event):
        self.changeVehicleFilter()

    def cbChangeVehicle(self, event):
        self.changeVehicle()

    def cbChangeTurret(self, event):
        self.changeTurret()

    def cbChangeModules(self, event):
        self.changeModules()


class PanelItem(object):
    def __init__(self, parent, label, unit, labelWidth=20, labelAnchor='e', valueWidth=6, valueAnchor='e'):
        self.__panel = tkinter.Frame(parent)
        self.__panel['borderwidth'] = 0
        self.__panel.pack(side='top', expand=1, fill='x', pady=1)
        self.__label = tkinter.Label(self.__panel, width=labelWidth, anchor=labelAnchor)
        self.__label['text'] = label
        self.__label.pack(side='left')
        self.__value = tkinter.Label(self.__panel, width=valueWidth, anchor=valueAnchor)
        self.__value.pack(side='left')
        self.__unit = tkinter.Label(self.__panel, width=5, anchor='w')
        self.__unit['text'] = unit
        self.__unit.pack(side='left')

    def setValue(self, value):
        self.__value['text'] = value
        #self.__value.delete(0, tkinter.END)
        #self.__value.insert(0, value)

class DropdownList(object):
    __values = [ '' ]

    def __init__(self, parent, width=None, label=None, labelwidth=None, valueJustify=None):
        self.__frame = tkinter.Frame(parent, padx=4)
        if label:
            self.__label = tkinter.Label(self.__frame, text=label, width=labelwidth, anchor='e')
            self.__label.pack(side='left')
        self.__combobox = tkinter.ttk.Combobox(self.__frame, state='readonly', justify=valueJustify)
        self.__combobox.pack(side='left')
        if width:
            self.setWidth(width)
    
    def pack(self, *args, **kvargs):
        self.__frame.pack(*args,**kvargs)

    def setWidth(self, value):
        self.__combobox['width'] = value

    def setCallback(self, cbFunc):
        self.__combobox.bind('<<ComboboxSelected>>', cbFunc)

    def setValues(self, labels, values):
        self.__values = values
        self.__combobox['values'] = labels
        self.__combobox.current(0)

    def getSelected(self):
        index = self.__combobox.current()
        return self.__values[index]


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

    app = Application()
    app.mainloop()
    
