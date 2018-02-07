import tkinter
import tkinter.ttk
import tkinter.font

import strage
import csvoutput

itemGroup = [
    {
        'title': None,
        'items': [
            'shell:damage_armor', 'shell:piercingPower',
            'gun:reloadTime', 'gun:aimingTime', 'gun:shotDispersionRadius'
        ]
    },
    {
        'title': 'DispersionFactor',
        'items': [
            'chassis:vehicleMovement', 'chassis:vehicleRotation', 'gun:turretRotation',
            'gun:afterShot', 'gun:whileGunDamaged'
        ]
    },
    {
        'title': None,
        'items': [
            'shell:damage_devices', 'shell:caliber', 'shell:speed', 'shell:maxDistance'
        ]
    }
]

class Application(tkinter.Frame):

    def __init__(self, master=None, strage=strage):
        self.__strage = strage

        self.__stragefetchInfo = {}
        self.__stragefetchInfo['vehicle'] = strage.fetchVehicleInfo
        self.__stragefetchInfo['chassis'] = strage.fetchChassisInfo
        self.__stragefetchInfo['turret'] = strage.fetchTurretInfo
        self.__stragefetchInfo['gun'] = strage.fetchGunInfo
        self.__stragefetchInfo['shell'] = strage.fetchShellInfo

        self.__stragefetchList = {}
        self.__stragefetchList['nation'] = strage.fetchNationList
        self.__stragefetchList['tier'] = strage.fetchTierList
        self.__stragefetchList['type'] = strage.fetchTypeList
        self.__stragefetchList['vehicle'] = strage.fetchVehicleList
        self.__stragefetchList['chassis'] = strage.fetchChassisList
        self.__stragefetchList['turret'] = strage.fetchTurretList
        self.__stragefetchList['gun'] = strage.fetchGunList
        self.__stragefetchList['shell'] = strage.fetchShellList

        self.__selector = {}

        tkinter.Frame.__init__(self, master)
        self.font = tkinter.font.Font(family='Arial', size=11, weight='normal')
        self.option_add('*font', self.font)
        self.option_add('*background', 'white')
        self.option_add('*relief', 'flat')
        self.master.title('Vehicle Selector')
        self.master.config(background='white', relief='flat')
        self.master.resizable(width=False, height=False)
        self.createWidgets()

        
    def createWidgets(self):
        bar = {}
        for group in [ 'vehicle', 'module', 'shell' ]:
            bar[group] = tkinter.Frame(self.master)
            bar[group].pack(side='top', expand=1, fill='x', padx=4, pady=1)

        modulePanel = tkinter.Frame(self.master, highlightthickness=1, highlightbackground='gray')
        modulePanel.pack(side='top', expand=1, fill='x', padx=8, pady=4)

        panelGroup = []
        for i in range(3):
            panel = tkinter.Frame(self.master, highlightthickness=1, highlightbackground='gray')
            panel.pack(side='top', expand=1, fill='x', padx=8, pady=4)
            panelGroup.append(panel)

        copyButton = tkinter.Button(self.master, text='copy to clipboard', command=self.createMessage, relief='ridge', borderwidth=2)
        copyButton.pack(side='top', expand=1, fill='x')
        
        option = {'label':{'text':'Nation'}, 'combobox':{'width':10}}
        selector = DropdownList(bar['vehicle'], name='nationSelector', option=option)
        selector.pack(side='left')
        selector.setValues(self.__stragefetchList['nation']())
        selector.setCallback(self.cbChangeVehicleFilter)
        self.__selector['nation'] = selector

        option = {'label':{'text':'Tier'}, 'combobox':{'width':3}, 'value':{'justify':'center'}}
        selector = DropdownList(bar['vehicle'], name='tierSelector', option=option)
        selector.pack(side='left')
        selector.setValues(self.__stragefetchList['tier']())
        selector.setCallback(self.cbChangeVehicleFilter)
        self.__selector['tier'] = selector

        option = {'label':{'text':'Type'}, 'combobox':{'width':4}, 'value':{'justify':'center'}}
        selector = DropdownList(bar['vehicle'], name='typeSelector', option=option)
        selector.pack(side='left')
        selector.setValues(self.__stragefetchList['type']())
        selector.setCallback(self.cbChangeVehicleFilter)
        self.__selector['type'] = selector

        option = {'label':{'text':'Vehicle'}, 'combobox':{'width':40}}
        selector = DropdownList(bar['vehicle'], option=option)
        selector.pack(side='left')
        selector.setCallback(self.cbChangeVehicle)
        self.__selector['vehicle'] = selector

        option = {'label':{'text':'Chassis'}, 'combobox':{'width':32}}
        selector = DropdownList(bar['module'], option=option)
        selector.pack(side='left')
        selector.setCallback(self.cbChangeModules)
        self.__selector['chassis'] = selector

        option={'label':{'text':'Turret'}, 'combobox':{'width':32}}
        selector = DropdownList(bar['module'], option=option)
        selector.pack(side='left')
        selector.setCallback(self.cbChangeTurret)
        self.__selector['turret'] = selector

        option={'label':{'text':'Gun'}, 'combobox':{'width':32}}
        selector = DropdownList(bar['module'], option=option)
        selector.pack(side='left')
        selector.setCallback(self.cbChangeGun)
        self.__selector['gun'] = selector

        option={'label':{'text':'Shell'}, 'combobox':{'width':32}}
        selector = DropdownList(bar['shell'], option=option)
        selector.pack(side='left')
        selector.setCallback(self.cbChangeModules)
        self.__selector['shell'] = selector
        
        self.__itemValue = {}
        opts = { 'label':{'width':8, 'anchor':'e'}, 'value':{'width':100, 'anchor':'w'} }
        for name in [ 'title:vehicle', 'title:chassis', 'title:turret', 'title:gun', 'title:shell' ]:
            self.__itemValue[name] = PanelItemValue(modulePanel, name, bind=self.getTitleValue, option=opts)

        opts = { 'label':{'width':20, 'anchor':'e'}, 'value':{'width':4, 'anchor':'e'}, 'unit':{'width':5, 'anchor':'w'} }
        for i, group in enumerate(itemGroup):
            if group['title'] is not None:
                PanelItemValue(panelGroup[i], None, option={'label':{'text':group['title'], 'width':20, 'anchor':'w'}})
            for item in group['items']:
                self.__itemValue[item] = PanelItemValue(panelGroup[i], item, bind=self.getItemValue, option=opts)
        self.changeVehicleFilter()


    def getTitleValue(self, target):
        category, node = target
        formatstring = csvoutput.items[category][node]['format']
        formattags = csvoutput.items[category][node]['value']
        tag = {}
        for s in [ 'nation', 'vehicle', 'chassis', 'turret', 'gun', 'shell' ]:
            tag[s] = self.__selector[s].getSelected()
        if tag['vehicle'] is None:
            return ''
        if node == 'vehicle':
            args = [ tag[s] for s in [ 'nation', 'vehicle' ] ]
        elif node == 'chassis':
            args = [ tag[s] for s in [ 'nation', 'vehicle', 'chassis' ] ]
        elif node == 'turret':
            args = [ tag[s] for s in [ 'nation', 'vehicle', 'turret' ] ]
        elif node == 'gun':
            args = [ tag[s] for s in [ 'nation', 'vehicle', 'turret', 'gun' ] ]
        elif node == 'shell':
            args = [ tag[s] for s in [ 'nation', 'gun', 'shell' ] ]
        values = self.__stragefetchInfo[node](*args)
        vlist = [ values[s] for s in formattags ]
        text = formatstring.format(*vlist)
        return text

    def getItemValue(self, target):
        category, node = target
        tag = {}
        for s in [ 'nation', 'vehicle', 'chassis', 'turret', 'gun', 'shell' ]:
            tag[s] = self.__selector[s].getSelected()
        if tag['vehicle'] is None:
            return ''
        if category == 'chassis':
            args = [ tag[s] for s in [ 'nation', 'vehicle', 'chassis' ] ]
        elif category == 'turret':
            args = [ tag[s] for s in [ 'nation', 'vehicle', 'turret' ] ]
        elif category == 'gun':
            args = [ tag[s] for s in [ 'nation', 'vehicle', 'turret', 'gun' ] ]
        elif category == 'shell':
            args = [ tag[s] for s in [ 'nation', 'gun', 'shell' ] ]
        text = self.__stragefetchInfo[category](*args)[node]
        return text

    def changeVehicleFilter(self):
        nation, tier, type = [ self.__selector[s].getSelected() for s in [ 'nation', 'tier', 'type' ] ]
        vehicles = self.__stragefetchList['vehicle'](nation, tier, type)
        if not vehicles or not vehicles[0]:
            vehicles = [ [ None, '' ] ]
        self.__selector['vehicle'].setValues(vehicles)
        self.changeVehicle()

    def changeVehicle(self):
        nation, vehicle = [ self.__selector[s].getSelected() for s in [ 'nation', 'vehicle' ] ]
        if vehicle:
            for s in [ 'chassis', 'turret' ]:
                self.__selector[s].setValues(self.__stragefetchList[s](nation, vehicle))
        else:
            for s in [ 'chassis', 'turret' ]:
                self.__selector[s].setValues([ [ None, '' ] ])
        self.changeTurret()

    def changeTurret(self):
        nation, vehicle = [ self.__selector[s].getSelected() for s in [ 'nation', 'vehicle' ] ]
        if vehicle:
            turret = self.__selector['turret'].getSelected()
            self.__selector['gun'].setValues(self.__stragefetchList['gun'](nation, vehicle, turret))
        else:
            self.__selector['gun'].setValues([ [ None, '' ] ])
        self.changeGun()

    def changeGun(self):
        nation, vehicle = [ self.__selector[s].getSelected() for s in [ 'nation', 'vehicle' ] ]
        if vehicle:
            gun = self.__selector['gun'].getSelected()
            self.__selector['shell'].setValues(self.__stragefetchList['shell'](nation, gun))
        else:
            self.__selector['shell'].setValues([ [ None, '' ] ])
        self.changeModules()

    def changeModules(self):
        for panel in self.__itemValue.values():
            panel.update()
 
 
    def createMessage(self):
        args = [ self.__selector[s].getSelected() for s in [ 'nation', 'vehicle', 'chassis', 'turret', 'gun', 'shell' ] ]       
        message = csvoutput.createMessage(self.__strage, *args)
        self.master.clipboard_clear()
        self.master.clipboard_append(message)


    def cbChangeVehicleFilter(self, event):
        self.changeVehicleFilter()

    def cbChangeVehicle(self, event):
        self.changeVehicle()

    def cbChangeTurret(self, event):
        self.changeTurret()

    def cbChangeGun(self, event):
        self.changeGun()

    def cbChangeModules(self, event):
        self.changeModules()


class PanelItemValue(tkinter.Frame):

    def __init__(self, master, name, *args, **kwargs):
        bind = kwargs.pop('bind', None)
        option = kwargs.pop('option', {})
        frameopt = { 'borderwidth':0 }
        frameopt.update(kwargs)
        super().__init__(master, *args, **frameopt)
        self.pack(side='top', fill='x', pady=0)
        labelopt = option['label'] if option is not None and 'label' in option else {}
        valueopt = option['value'] if option is not None and 'value' in option else {}
        unitopt = option['unit'] if option is not None and 'unit' in option else {}
        self.__label = tkinter.Label(self, **labelopt)
        self.__label.pack(side='left')
        if name is not None:
            category, node = name.split(':')
            self.__bind = { 'category':category, 'node':node, 'target':[category, node], 'func':bind }
            self.__label['text'] = csvoutput.items[category][node]['label']
            self.__value = tkinter.Label(self, **valueopt)
            self.__value.pack(side='left')
            if 'unit' in csvoutput.items[category][node]:
                self.__unit = tkinter.Label(self, **unitopt)
                self.__unit['text'] = csvoutput.items[category][node]['unit']
                self.__unit.pack(side='left')

    def update(self):
        text = self.__bind['func'](self.__bind['target'])
        self.__value['text'] = text


class DropdownList(tkinter.Frame):
    __values = [ '' ]

    def __init__(self, master, *args, **kwargs):
        option = kwargs.pop('option', {})
        frameopt = { 'borderwidth':0, 'padx':4 }
        frameopt.update(kwargs)
        cboxopt = {}
        if 'combobox' in option:
            cboxopt.update(option['combobox'])
        super().__init__(master, *args, **frameopt)
        if 'label' in option:
            self.__label = tkinter.Label(self, **option['label'])
            self.__label.pack(side='left')
        self.__combobox = tkinter.ttk.Combobox(self, state='readonly', **cboxopt)
        self.__combobox.pack(side='left')
        name = str(self).split('.')[-1]
        if 'value' in option and 'justify' in option['value']:
            self.option_add('*' + name + '*justify', option['value']['justify'])
    
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
    
