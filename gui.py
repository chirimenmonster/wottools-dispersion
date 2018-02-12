import tkinter
import tkinter.ttk
import tkinter.font

from lib.strage import Strage
from lib import csvoutput
from lib.resources import g_resources, NATIONS, TIERS, TYPES
from lib.config import parseArgument, g_config as config

class Application(tkinter.Frame):

    def __init__(self, master=None, strage=None):
        self.__itemgroup = g_resources.itemgroup
        self.__titlesdesc = g_resources.titlesdesc
        self.__selectorsdesc = g_resources.selectorsdesc

        self.__strage = strage

        self.__stragefetchList = {}
        self.__stragefetchList['nation'] = strage.fetchNationList
        self.__stragefetchList['tier'] = strage.fetchTierList
        self.__stragefetchList['type'] = strage.fetchTypeList
        self.__stragefetchList['vehicle'] = strage.fetchVehicleList
        self.__stragefetchList['chassis'] = strage.fetchChassisList
        self.__stragefetchList['turret'] = strage.fetchTurretList
        self.__stragefetchList['engine'] = strage.fetchEngineList
        self.__stragefetchList['radio'] = strage.fetchRadioList
        self.__stragefetchList['gun'] = strage.fetchGunList
        self.__stragefetchList['shell'] = strage.fetchShellList
        self.__stragefetchList['siege'] = strage.fetchSiegeList

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
                selector = DropdownList(bar, name=name, entry=entry, method=self.getDropdownList, option=option, selected=selected)
                if 'attr' in entry and entry['attr'] == 'const':
                    selector.update()
                selector.setCallback(self.__selectorCB[entry['callback']])
                selector.pack()
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

    def packSelectors(self):
        for panel in self.__selectorList:
            panel.pack()

    def packTitleDesc(self):
        for panel in self.__vehicleDescs:
            panel.pack()

    def packItemGroup(self):
        for panel in self.__itemValues:
            panel.pack()

    def getDropdownList(self, schema):
        param = {}
        if 'attr' not in schema or not schema['attr'] == 'const':
            for s in [ 'nation', 'tier', 'type', 'vehicle', 'chassis', 'turret', 'engine', 'radio', 'gun', 'shell', 'siege' ]:
                param[s] = self.__selector[s].getSelected()
        result = self.__strage.getDropdownList(schema, param)
        if result is None or result == []:
            result = [ [ None, '' ] ]
        return result

    def getVehicleValue(self, schema):
        param = {}
        for s in [ 'nation', 'vehicle', 'chassis', 'turret', 'engine', 'radio', 'gun', 'shell', 'siege' ]:
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
        param = {}
        for category in  [ 'nation', 'vehicle', 'chassis', 'turret', 'engine', 'radio', 'gun', 'shell', 'siege' ]:
            param[category] = self.__selector[category].getSelected()

        values = []
        for schema in self.__titlesdesc:
            value = []
            for item in schema['value']:
                value.append(self.__strage.find(item, param))
            values.append([ schema['label'], *value ])

        values.append([ 'Siege:', param['siege'] or 'None' ])

        for column in self.__itemgroup:
            for row in column:
                for schema in row['items']:
                    value = self.__strage.find(schema['value'], param)
                    values.append([ schema['label'], value, schema.get('unit', ''), schema['value'] ])

        message = csvoutput.createMessage(self.__strage, values)
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
    __values = [ None ]

    def __init__(self, master, *args, entry=None, method=None, option=None, selected=None, **kwargs):
        self.__target = entry
        self.__method = method
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

    def update(self):
        list = self.__method(self.__target)
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

    def pack(self):
        super().pack_forget()
        if self.__target.get('attr', None) == 'phantom':
            if not self.__values[-1]:
                return
        super().pack(side='left')


if __name__ == '__main__':
    import io, sys
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    parseArgument()

    app = Application(strage=Strage())
    app.mainloop()
    
