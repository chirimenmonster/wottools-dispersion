import tkinter
import tkinter.ttk
import tkinter.font

import strage

class Application(tkinter.Frame):

    def __init__(self, master=None, strage=strage):
        self.__strage = strage
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

        copyButton = tkinter.Button(self.master, text='copy to clipboard', command=self.createMessage, relief='ridge', borderwidth=2)
        copyButton.pack(side='top', expand=1, fill='x')
        
        self.__nationSelector = DropdownList(vehicleSelectorBar, width=10, label='Nation', name='nationSelector', valueJustify='center')
        self.__nationSelector.pack(side='left')
        self.__nationSelector.setValues(self.__strage.fetchNationList())
        self.__nationSelector.setCallback(self.cbChangeVehicleFilter)

        self.__tierSelector = DropdownList(vehicleSelectorBar, width=3, label='Tier', name='tierSelector', valueJustify='center')
        self.__tierSelector.pack(side='left')
        self.__tierSelector.setValues(self.__strage.fetchTierList())
        self.__tierSelector.setCallback(self.cbChangeVehicleFilter)

        self.__typeSelector = DropdownList(vehicleSelectorBar, width=4, label='Type', name='typeSelector', valueJustify='center')
        self.__typeSelector.pack(side='left')
        self.__typeSelector.setValues(self.__strage.fetchTypeList())
        self.__typeSelector.setCallback(self.cbChangeVehicleFilter)

        self.__vehicleSelector = DropdownList(vehicleSelectorBar, width=40, label='Vehicle')
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
        self.__item['vehicle'] = PanelItem(modulePanel, 'Vehicle:', '', labelWidth=8, valueWidth=100, valueAnchor='w')
        self.__item['chassis'] = PanelItem(modulePanel, 'Chassis:', '', labelWidth=8, valueWidth=60, valueAnchor='w')
        self.__item['turret'] = PanelItem(modulePanel, 'Turret:', '', labelWidth=8, valueWidth=60, valueAnchor='w')
        self.__item['gun'] = PanelItem(modulePanel, 'Gun:', '', labelWidth=8, valueWidth=60, valueAnchor='w')
        self.__item['reloadTime'] = PanelItem(itemPanel, 'reload time:', 's', valueWidth=4)
        self.__item['aimingTime'] = PanelItem(itemPanel, 'aiming time:', 's', valueWidth=4)
        self.__item['shotDispersionRadius'] = PanelItem(itemPanel, 'shot dispersion radius:', 'm', valueWidth=4)
        PanelItem(itemPanel, 'DispersionFactor', '', labelAnchor='w')
        self.__item['vehicleMovement'] = PanelItem(itemPanel, '... vehicle movement:', '', valueWidth=4)
        self.__item['vehicleRotation'] = PanelItem(itemPanel, '... vehicle rotation:', '', valueWidth=4)
        self.__item['turretRotation'] = PanelItem(itemPanel, '... turret rotation:', '', valueWidth=4)
        self.__item['afterShot'] = PanelItem(itemPanel, '... after shot:', '', valueWidth=4)
        self.__item['whileGunDamaged'] = PanelItem(itemPanel, '... while gun damaged:', '', valueWidth=4)

        self.changeVehicleFilter()
        self.changeVehicle()
        self.changeModules()

    def changeVehicleFilter(self):
        nation = self.__nationSelector.getSelected()
        tier = self.__tierSelector.getSelected()
        type = self.__typeSelector.getSelected()
        vehicles = self.__strage.fetchVehicleList(nation, tier, type)
        if not vehicles or not vehicles[0]:
            vehicles = [ [ None, '' ] ]
        self.__vehicleSelector.setValues(vehicles)
        self.changeVehicle()

    def changeVehicle(self):
        nation = self.__nationSelector.getSelected()
        vehicleId = self.__vehicleSelector.getSelected()
        if vehicleId:
            vehicleInfo = self.__strage.fetchVehicleInfo(nation, vehicleId)
            self.__chassisSelector.setValues(self.__strage.fetchChassisList(nation, vehicleId))
            self.__turretSelector.setValues(self.__strage.fetchTurretList(nation, vehicleId))
        else:
            self.__chassisSelector.setValues([ [ None, '' ] ])
            self.__turretSelector.setValues([ [ None, '' ] ])
        self.changeTurret()

    def changeTurret(self):
        nation = self.__nationSelector.getSelected()
        vehicleId = self.__vehicleSelector.getSelected()
        if vehicleId:
            turretTag = self.__turretSelector.getSelected()
            self.__gunSelector.setValues(self.__strage.fetchGunList(nation, vehicleId, turretTag))
        else:
            self.__gunSelector.setValues([ [ None, '' ] ])
        self.changeModules()

    def changeModules(self):
        nation = self.__nationSelector.getSelected()
        vehicleId = self.__vehicleSelector.getSelected()
        if vehicleId:
            vehicleInfo = self.__strage.fetchVehicleInfo(nation, vehicleId)
            self.__item['vehicle'].setValue('{} ({}), {}: {}'.format(vehicleInfo['name'], vehicleInfo['id'], vehicleInfo['shortUserString'], vehicleInfo['description']))
            chassisTag = self.__chassisSelector.getSelected()
            turretTag = self.__turretSelector.getSelected()
            gunTag = self.__gunSelector.getSelected()
            chassis = self.__strage.fetchChassisInfo(nation, vehicleId, chassisTag)
            turret = self.__strage.fetchTurretInfo(nation, vehicleId, turretTag)
            gun = self.__strage.fetchGunInfo(nation, vehicleId, turretTag, gunTag)
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
 
    def createMessage(self):
        import io
        import csv
        output = io.StringIO(newline='')
        writer = csv.writer(output, dialect='excel', lineterminator='\n')
        
        nation = self.__nationSelector.getSelected()
        vehicleId = self.__vehicleSelector.getSelected()
        chassisTag = self.__chassisSelector.getSelected()
        turretTag = self.__turretSelector.getSelected()
        gunTag = self.__gunSelector.getSelected()
        vehicleInfo = self.__strage.fetchVehicleInfo(nation, vehicleId)
        chassis = self.__strage.fetchChassisInfo(nation, vehicleId, chassisTag)
        turret = self.__strage.fetchTurretInfo(nation, vehicleId, turretTag)
        gun = self.__strage.fetchGunInfo(nation, vehicleId, turretTag, gunTag)
        
        writer.writerow([ 'vehicle', vehicleInfo['name'], vehicleInfo['id'], vehicleInfo['shortUserString'], vehicleInfo['description'] ])
        writer.writerow([ 'chassis', chassis['name'], chassis['tag'] ])
        writer.writerow([ 'turret', turret['name'], turret['tag'] ])
        writer.writerow([ 'gun', gun['name'], gun['tag'] ])
        writer.writerow([ 'reloadTime', gun['reloadTime'], 's' ])
        writer.writerow([ 'aimingTime', gun['aimingTime'], 's' ])
        writer.writerow([ 'shotDispersionRadius', gun['shotDispersionRadius'], 'm' ])
        writer.writerow([ 'vehicleMovement', chassis['vehicleMovement'], '' ])
        writer.writerow([ 'vehicleRotation', chassis['vehicleRotation'], '' ])
        writer.writerow([ 'turretRotation', gun['turretRotation'], '' ])
        writer.writerow([ 'afterShot', gun['afterShot'], '' ])
        writer.writerow([ 'whileGunDamaged', gun['whileGunDamaged'], '' ])

        self.master.clipboard_clear()
        self.master.clipboard_append(output.getvalue())
        output.close()

    def cbChangeVehicleFilter(self, event):
        self.changeVehicleFilter()

    def cbChangeVehicle(self, event):
        self.changeVehicle()

    def cbChangeTurret(self, event):
        self.changeTurret()

    def cbChangeModules(self, event):
        self.changeModules()


class PanelItem(object):
    def __init__(self, parent, label, unit, labelWidth=20, labelAnchor='e', valueWidth=None, valueAnchor='e'):
        self.__panel = tkinter.Frame(parent)
        self.__panel['borderwidth'] = 0
        self.__panel.pack(side='top', fill='x', pady=1)
        self.__label = tkinter.Label(self.__panel, width=labelWidth, anchor=labelAnchor)
        self.__label['text'] = label
        self.__label.pack(side='left')
        self.__value = tkinter.Label(self.__panel, width=valueWidth, anchor=valueAnchor)
        self.__value.pack(side='left')
        if unit:
            self.__unit = tkinter.Label(self.__panel, width=5, anchor='w')
            self.__unit['text'] = unit
            self.__unit.pack(side='left')

    def setValue(self, value):
        self.__value['text'] = value

class DropdownList(object):
    __values = [ '' ]

    def __init__(self, parent, width=None, label=None, labelwidth=None, valueJustify=None, name=None):
        self.__frame = tkinter.Frame(parent, padx=4, name=name)
        if label:
            self.__label = tkinter.Label(self.__frame, text=label, width=labelwidth, anchor='e')
            self.__label.pack(side='left')
        self.__combobox = tkinter.ttk.Combobox(self.__frame, state='readonly', width=width, justify=valueJustify)
        self.__combobox.pack(side='left')
        if name and valueJustify:
            self.__label.option_add('*' + name + '*justify', valueJustify)
    
    def pack(self, *args, **kvargs):
        self.__frame.pack(*args,**kvargs)

    def setWidth(self, value):
        self.__combobox['width'] = value

    def setCallback(self, cbFunc):
        self.__combobox.bind('<<ComboboxSelected>>', cbFunc)

    def setValues(self, list):
        self.__values = [ t[0] for t in list ]
        self.__combobox['values'] = [ t[1] for t in list ]
        self.__combobox.current(0)

    def getSelected(self):
        index = self.__combobox.current()
        return self.__values[index]


if __name__ == '__main__':
    import io, sys
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    strage.parseArgument()

    app = Application(strage=strage.Strage())
    app.mainloop()
    
