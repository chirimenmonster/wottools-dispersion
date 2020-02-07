from functools import partial

import tkinter
import tkinter.ttk
import tkinter.font

from lib import csvoutput
from lib.resources import g_resources
from lib.config import parseArgument, g_config as config

from lib.application import g_application as app
from lib.dropdownlist import DropdownList as DropdownList2

class Application(tkinter.Frame):

    def __init__(self, master=None, strage=None):
        self.__strage = strage

        self.__itemgroup = g_resources.itemgroup
        self.__titlesdesc = g_resources.titlesdesc
        self.__selectorsdesc = g_resources.selectorsdesc

        self.__handlerChangeSelected = {
            'vehicleFilter':    self.changeVehicleFilter,
            'vehicle':          self.changeVehicle,
            'turret':           self.changeTurret,
            'gun':              self.changeGun,
            'modules':          self.changeModules
        }
        
        config.GUI_DIR = 'test/data/res'
        config.scriptspkg = 'test/data/res/packages/scripts.pkg'
        config.schema = 'test/data/itemschema.json'
        config.localedir = 'test/data/res'
        app.setup(config)
        app.dropdownlist = DropdownList2()
        
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
        self.createSpecView(self.master, self.__itemgroup, None)
        self.createCommandView(self.master)

        if config.vehicle is not None:
            param = self.__strage.getParamFromVehicle(config.vehicle)
        else:
            param = None

        self.packTitleDesc()
        self.changeVehicleFilter(param)

    def createSelectorBars(self, master):
        self.__selectorSchema = {}
        self.__selector = {}
        self.__selectorList = []
        for row in self.__selectorsdesc:
            bar = tkinter.Frame(master)
            bar.pack(side='top', expand=1, fill='x', padx=4, pady=1)
            for entry in row:
                option = entry['option']
                name = entry['id'] + 'Selector'
                selected = entry['selected'] if 'selected' in entry else None
                #selector = DropdownList(bar, name=name, entry=entry, method=self.getDropdownList, option=option, selected=selected)
                selector = DropdownList(bar, name=name, entry=entry, method=self.getDropdownList2, option=option, selected=selected)
                if 'attr' in entry and entry['attr'] == 'const':
                    selector.update()
                callback = lambda self, id, event : self.__handlerChangeSelected[id]()
                selector.setCallback(partial(callback, self, entry['callback']))
                self.__selectorSchema[entry['id']] = entry
                self.__selector[entry['id']] = selector 
                self.__selectorList.append(selector)

    def createDescriptionView(self, master):
        view = tkinter.Frame(master, highlightthickness=1, highlightbackground='gray')
        view.pack(side='top', expand=1, fill='x', padx=8, pady=4)
        opts = { 'label':{'width':8, 'anchor':'e'}, 'value':{'width':100, 'anchor':'w'} }
        self.__vehicleDescs = []
        for entry in self.__titlesdesc:
            panel = PanelItemValue(view, entry, self.getVehicleValue, option=opts)
            self.__vehicleDescs.append(panel)

    def createSpecView(self, master, target, option):
        self.__itemValues = []
        panel = tkinter.Frame(master)
        panel.pack(side='top', expand=1, fill='x')
        option = target.get('guioption', option)
        for column in target.get('columns', []):
            self.createSpecViewColumn(panel, column, option)

    def createSpecViewColumn(self, master, target, option):
        panel = tkinter.Frame(master)
        panel.pack(side='left', anchor='n')
        option = target.get('guioption', option)
        for row in target.get('rows', []):
            self.createSpecViewRow(panel, row, option)

    def createSpecViewRow(self, master, target, option):
        panel = tkinter.Frame(master, highlightthickness=1, highlightbackground='gray')
        panel.pack(side='top', expand=1, padx=8, pady=2, anchor='w')
        option = target.get('guioption', option)
        for item in target.get('items', []):
            self.createSpecViewItem(panel, item, option)
        
    def createSpecViewItem(self, master, target, option):
        option = target.get('guioption', option)
        panel = PanelItemValue(master, target, self.getVehicleValue, option=option)
        self.__itemValues.append(panel)

    def createCommandView(self, master):
        label = 'copy to clipboard'
        option = {'relief':'ridge', 'borderwidth':2}
        copyButton = tkinter.Button(master, text=label, command=self.createMessage, **option)
        copyButton.pack(side='top', expand=1, fill='x', padx=7, pady=2)   

    def packSelectors(self):
        for panel in self.__selectorList:
            panel.pack()

    def packTitleDesc(self):
        for panel in self.__vehicleDescs:
            panel.pack()

    def packItemGroup(self):
        for panel in self.__itemValues:
            panel.pack()

    def getSelectedValues(self):
        param = {}
        for id, selector in self.__selector.items():
            param[id] = selector.getSelected()
        return param
 
    def getDropdownList2(self, schema):
        param = self.getSelectedValues()
        category = schema['id']
        if category == 'nation':
            result = app.dropdownlist.fetchNationList(param=param)
        elif category == 'tier':
            result = app.dropdownlist.fetchTierList(param=param)
        elif category == 'type':
            result = app.dropdownlist.fetchTypeList(param=param)
        elif category == 'vehicle':
            result = app.dropdownlist.fetchVehicleList(param=param)
        elif param['vehicle'] is None:
            result = None
        else:
            for k,v in {'chassis':-1, 'turret':-1, 'engine':-1, 'radio':-1, 'gun':-1, 'shell':1 }.items():
                if param.get(k, None) is None:
                    param[k] = v
            if category == 'chassis':
                result = app.dropdownlist.fetchChassisList(param=param)
            elif category == 'turret':
                result = app.dropdownlist.fetchTurretList(param=param)
            elif category == 'engine':
                result = app.dropdownlist.fetchEngineList(param=param)
            elif category == 'radio':
                result = app.dropdownlist.fetchRadioList(param=param)
            elif category == 'gun':
                result = app.dropdownlist.fetchGunList(param=param)
            elif category == 'shell':
                result = app.dropdownlist.fetchShellList(param=param)
            elif category == 'siege':
                result = [['', ''], ['siege', 'siege']]
            else:
                raise NotImplementedError
        if result is None or result == []:
            result = [ [ None, '' ] ]
        return result
        
    def getDropdownList(self, schema):
        param = self.getSelectedValues()
        result = self.__strage.getDropdownList(schema, param)
        if result is None or result == []:
            result = [ [ None, '' ] ]
        return result

    def getVehicleValue(self, schema):
        param = self.getSelectedValues()
        text = self.__strage.findText(schema, param)
        return text

    def changeVehicleFilter(self, param=None):
        if param is not None:
            self.__selector['nation'].select(param['nation'])
            self.__selector['tier'].select(param['tier'])
            self.__selector['type'].select(param['type'])
        self.__selector['vehicle'].update()
        self.changeVehicle()

    def changeVehicle(self):
        for s in [ 'chassis', 'turret', 'engine', 'radio', 'siege' ]:
            self.__selector[s].update()
        self.changeTurret()

    def changeTurret(self):
        self.__selector['gun'].update()
        self.changeGun()

    def changeGun(self):
        self.__selector['shell'].update()
        self.changeModules()

    def changeModules(self):
        for panel in self.__vehicleDescs:
            panel.update()
        for panel in self.__itemValues:
            panel.update()
        self.packSelectors()
        self.packItemGroup()

    def createMessage(self):
        param = self.getSelectedValues()
        values = self.__strage.getDescription(param)
        message = csvoutput.createMessage(self.__strage, values)
        self.master.clipboard_clear()
        self.master.clipboard_append(message)


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

    def __init__(self, master, *args, entry=None, method=None, option=None, selected=None, **kwargs):
        self.__target = entry
        self.__method = method
        self.__defaultSelected = selected
        self.__values = [ None ]
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

    def update(self):
        list = self.__method(self.__target)
        self.__values = [ t[0] for t in list ]
        self.__combobox['values'] = [ t[1] for t in list ]
        name = str(self).split('.')[-1]
        if self.__defaultSelected == 'last':
            self.__combobox.current(len(list) - 1)
        else:
            self.__combobox.current(0)

    def select(self, value):
        index = self.__values.index(value)
        self.__combobox.current(index)
    
    def getSelected(self):
        index = self.__combobox.current()
        return self.__values[index]

    def pack(self):
        super().pack_forget()
        if self.__target.get('attr', None) == 'phantom':
            if not self.__values[-1]:
                return
        super().pack(side='left')

