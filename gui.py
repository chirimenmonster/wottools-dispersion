import tkinter
import tkinter.ttk
import tkinter.font

import json

import strage
import csvoutput

class Application(tkinter.Frame):

    def __init__(self, master=None, strage=strage):
        with open('itemdef.json', 'r') as fp:
            self.__itemdef = json.load(fp)
        with open('guidef.json', 'r') as fp:
            self.__itemgroup = json.load(fp)

        self.__strage = strage

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
        self.font = tkinter.font.Font(family='Arial', size=10, weight='normal')
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

        panelZone = tkinter.Frame(self.master)
        panelZone.pack(side='top', expand=1, fill='x')

        copyButton = tkinter.Button(self.master, text='copy to clipboard', command=self.createMessage, relief='ridge', borderwidth=2)
        copyButton.pack(side='top', expand=1, fill='x', padx=7, pady=4)
        
        panelColumn = []
        for i in range(3):
            panel = tkinter.Frame(panelZone)
            panel.pack(side='left', anchor='n')
            panelColumn.append(panel)

        panelGroup = []
        for i, column in enumerate(self.__itemgroup):
            panelGroup.append([])
            for j, row in enumerate(column):
                panel = tkinter.Frame(panelColumn[i], highlightthickness=1, highlightbackground='gray')
                panel.pack(side='top', expand=1, padx=8, pady=4, anchor='w')
                panelGroup[i].append(panel)
        
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
            self.__itemValue[name] = PanelItemValue(modulePanel, name, self.__itemdef, bind=self.getTitleValue, option=opts)

        for i, column in enumerate(self.__itemgroup):
            for j, row in enumerate(column):
                if row['title'] is not None:
                    opts = { k:v for k,v in row['titleoption'].items() }
                    opts['label']['text'] = row['title']
                    PanelItemValue(panelGroup[i][j], None, self.__itemdef, option=opts)
                for item in row['items']:
                    self.__itemValue[item] = PanelItemValue(panelGroup[i][j], item, self.__itemdef, bind=self.getItemValue, option=row['option'])
        self.changeVehicleFilter()


    def getTitleValue(self, target):
        category, node = target
        param = {}
        for s in [ 'nation', 'vehicle', 'chassis', 'turret', 'gun', 'shell' ]:
            param[s] = self.__selector[s].getSelected()
        if param['vehicle'] is None:
            return ''
        text = self.__strage.getDescription(node, param)
        return text

    def getItemValue(self, target):
        category, node = target
        param = {}
        for s in [ 'nation', 'vehicle', 'chassis', 'turret', 'gun', 'shell' ]:
            param[s] = self.__selector[s].getSelected()
        if param['vehicle'] is None:
            return ''
        text = self.__strage.find(category, node, param)
        return text or ''

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
        param = {}
        for category in  [ 'nation', 'vehicle', 'chassis', 'turret', 'gun', 'shell' ]:
            param[category] = self.__selector[category].getSelected()
        items = []
        for column in self.__itemgroup:
            for row in column:
                items += row['items']
        message = csvoutput.createMessage(self.__strage, param, items)
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

    def __init__(self, master, name, itemdef, *args, **kwargs):
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
            self.__label['text'] = itemdef[category][node]['label']
            self.__value = tkinter.Label(self, **valueopt)
            self.__value.pack(side='left')
            if 'unit' in itemdef[category][node]:
                self.__unit = tkinter.Label(self, **unitopt)
                self.__unit['text'] = itemdef[category][node]['unit']
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
    
