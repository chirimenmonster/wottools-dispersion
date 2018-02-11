from functools import partial

import tkinter
import tkinter.ttk
import tkinter.font

import json

import strage
import csvoutput

class Application(tkinter.Frame):

    def __init__(self, master=None, strage=strage):
        with open('guisettings_items.json', 'r') as fp:
            self.__itemgroup = json.load(fp)
        with open('guisettings_titles.json', 'r') as fp:
            self.__titlesdesc = json.load(fp)
        with open('guisettings_selectors.json', 'r') as fp:
            self.__selectorsdesc = json.load(fp)

        self.__strage = strage

        self.__stragefetchList = {}
        self.__stragefetchList['nation'] = strage.fetchNationList
        self.__stragefetchList['tier'] = strage.fetchTierList
        self.__stragefetchList['type'] = strage.fetchTypeList
        self.__stragefetchList['vehicle'] = strage.fetchVehicleList
        self.__stragefetchList['chassis'] = strage.fetchChassisList
        self.__stragefetchList['turret'] = strage.fetchTurretList
        self.__stragefetchList['engine'] = strage.fetchEngineList
        self.__stragefetchList['fueltank'] = strage.fetchFueltankList
        self.__stragefetchList['radio'] = strage.fetchRadioList
        self.__stragefetchList['gun'] = strage.fetchGunList
        self.__stragefetchList['shell'] = strage.fetchShellList

        self.__selector = {}

        self.__selectorCB = {}
        self.__selectorCB['vehicleFilter'] = self.cbChangeVehicleFilter
        self.__selectorCB['vehicle'] = self.cbChangeVehicle
        self.__selectorCB['turret'] = self.cbChangeTurret
        self.__selectorCB['gun'] = self.cbChangeGun
        self.__selectorCB['modules'] = self.cbChangeModules
        
        tkinter.Frame.__init__(self, master)
        self.font = tkinter.font.Font(family='Arial', size=10, weight='normal')
        self.option_add('*font', self.font)
        self.option_add('*background', 'white')
        self.option_add('*relief', 'flat')
        self.master.title('Vehicle Selector')
        self.master.config(background='white', relief='flat')
        self.master.resizable(width=False, height=False)

        self.createSelectorBars(self.master)
        self.createDescriptionView(self.master)
        self.createSpecView(self.master)
        self.createCommandView(self.master)

        self.packTitleDesc()
        self.changeVehicleFilter()

    def createSelectorBars(self, master):
        self.__selector = {}
        for row in self.__selectorsdesc:
            bar = tkinter.Frame(master)
            bar.pack(side='top', expand=1, fill='x', padx=4, pady=1)
            for entry in row:
                option = entry['option']
                name = entry['id'] + 'Selector'
                selected = entry['selected'] if 'selected' in entry else None
                selector = DropdownList(bar, name=name, option=option, selected=selected)
                if 'attr' in entry and entry['attr'] == 'const':
                    selector.setValues(self.__stragefetchList[entry['id']]())
                selector.setCallback(self.__selectorCB[entry['callback']])
                selector.pack(side='left')
                self.__selector[entry['id']] = selector 

    def createDescriptionView(self, master):
        view = tkinter.Frame(master, highlightthickness=1, highlightbackground='gray')
        view.pack(side='top', expand=1, fill='x', padx=8, pady=4)
        opts = { 'label':{'width':8, 'anchor':'e'}, 'value':{'width':100, 'anchor':'w'} }
        self.__vehicleDescs = []
        for entry in self.__titlesdesc:
            panel = PanelItemValue(view, entry, self.getVehicleValue, option=opts)
            self.__vehicleDescs.append(panel)

    def createSpecView(self, master):
        view = tkinter.Frame(master)
        view.pack(side='top', expand=1, fill='x')
        self.__itemValues = []
        for itemsColumn in self.__itemgroup:
            viewColumn = tkinter.Frame(view)
            viewColumn.pack(side='left', anchor='n')
            for itemsRow in itemsColumn:
                viewRow = tkinter.Frame(viewColumn, highlightthickness=1, highlightbackground='gray')
                viewRow.pack(side='top', expand=1, padx=8, pady=2, anchor='w')
                for entry in itemsRow['items']:
                    panel = PanelItemValue(viewRow, entry, self.getVehicleValue, option=itemsRow['option'])
                    self.__itemValues.append(panel)

    def createCommandView(self, master):
        label = 'copy to clipboard'
        option = {'relief':'ridge', 'borderwidth':2}
        copyButton = tkinter.Button(master, text=label, command=self.createMessage, **option)
        copyButton.pack(side='top', expand=1, fill='x', padx=7, pady=2)   

    def packTitleDesc(self):
        for panel in self.__vehicleDescs:
            panel.pack()

    def packItemGroup(self):
        for panel in self.__itemValues:
            panel.pack()

    def getVehicleValue(self, schema):
        param = {}
        for s in [ 'nation', 'vehicle', 'chassis', 'turret', 'engine', 'fueltank', 'radio', 'gun', 'shell' ]:
            param[s] = self.__selector[s].getSelected()
        if param['vehicle'] is None:
            return ''
        if isinstance(schema['value'], list):
            values = []
            for item in schema['value']:
                values.append(self.__strage.find(item, param))
            text = schema['format'].format(*values)
        elif isinstance(schema['value'], str):
            value = self.__strage.find(schema['value'], param)
            if 'consider' in schema:
                if schema['consider'] == 'float':
                    value = float(value)
            if 'format' in schema:
                text = schema['format'].format(value)
            else:
                text = value
        else:
            print('not implements')
            raise ValueError
        return text or ''

    def changeVehicleFilter(self):
        nation, tier, type = [ self.__selector[s].getSelected() for s in [ 'nation', 'tier', 'type' ] ]
        args = [ nation, tier, type ]
        vehicles = self.__stragefetchList['vehicle'](*args)
        if not vehicles or not vehicles[0]:
            vehicles = [ [ None, '' ] ]
        self.__selector['vehicle'].setValues(vehicles)
        self.changeVehicle()

    def changeVehicle(self):
        nation, vehicle = [ self.__selector[s].getSelected() for s in [ 'nation', 'vehicle' ] ]
        args = [ nation, vehicle ]
        for s in [ 'chassis', 'turret', 'engine', 'fueltank', 'radio' ]:
            if None not in args:
                values = self.__stragefetchList[s](*args)
            else:
                values = [ [ None, '' ] ]
            self.__selector[s].setValues(values)
        self.changeTurret()

    def changeTurret(self):
        nation, vehicle, turret = [ self.__selector[s].getSelected() for s in [ 'nation', 'vehicle', 'turret' ] ]
        args = [ nation, vehicle, turret ]
        if None not in args:
            values = self.__stragefetchList['gun'](*args)
        else:
            values = [ [ None, '' ] ]
        self.__selector['gun'].setValues(values)
        self.changeGun()

    def changeGun(self):
        nation, gun = [ self.__selector[s].getSelected() for s in [ 'nation', 'gun' ] ]
        args = [ nation, gun ]
        if None not in args:
            values = self.__stragefetchList['shell'](*args)
        else:
            values = [ [ None, '' ] ]
        self.__selector['shell'].setValues(values)
        self.changeModules()

    def changeModules(self):
        for panel in self.__vehicleDescs:
            panel.update()
        for panel in self.__itemValues:
            panel.update()
        self.packItemGroup()

    def createMessage(self):
        param = {}
        for category in  [ 'nation', 'vehicle', 'chassis', 'turret', 'engine', 'fueltank', 'radio', 'gun', 'shell' ]:
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

    def __init__(self, master, target, method, *args, option=None, **kwargs):
        self.__target = target
        self.__method = method
        frameopt = { 'borderwidth':0 }
        frameopt.update(kwargs)
        super().__init__(master, *args, **frameopt)
        labelopt = option['label'] if option is not None and 'label' in option else {}
        valueopt = option['value'] if option is not None and 'value' in option else {}
        unitopt = option['unit'] if option is not None and 'unit' in option else {}
        self.__label = tkinter.Label(self, **labelopt)
        self.__label['text'] = target['label']
        self.__label.pack(side='left')
        self.__value = tkinter.Label(self, **valueopt)
        self.__value.pack(side='left')
        if 'unit' in target:
            self.__unit = tkinter.Label(self, **unitopt)
            self.__unit['text'] = target['unit']
            self.__unit.pack(side='left')

    def pack(self):
        super().pack_forget()
        if self.__target and 'attr' in self.__target:
            if self.__target['attr'] == 'phantom':
                value = self.__value['text']
                if value is None or value == '':
                    return
        super().pack(side='top', fill='x', pady=0)

    def update(self):
        text = self.__method(self.__target)
        if text is None:
            text = ''
        self.__value['text'] = text


class DropdownList(tkinter.Frame):
    __values = [ '' ]

    def __init__(self, master, *args, option=None, selected=None, **kwargs):
        self.__defaultSelected = selected
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
        name = str(self).split('.')[-1]
        if self.__defaultSelected == 'last':
            self.__combobox.current(len(list) - 1)
        else:
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
    
