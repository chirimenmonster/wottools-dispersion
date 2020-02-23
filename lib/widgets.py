from functools import partial

import tkinter
import tkinter.ttk
import tkinter.font

from lib.output import getOutputCsv
from lib.wselector import SelectorPanel
from lib.wdescription import SpecViewItem, g_data


class GuiApplication(tkinter.Frame):

    def __init__(self, app, master=None):
        super(GuiApplication, self).__init__(master)
        self.__app = app

        self.__itemgroup = app.settings.guiitems
        self.__titlesdesc = app.settings.guititles
        self.__selectorsdesc = app.settings.guiselectors

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

        self.packTitleDesc()

        self.__app.widgets['!vehicleselector'].onSelected.append(self.changeSpec)
        self.__app.widgets['!chassisselector'].onSelected.append(self.changeSpec)
        self.__app.widgets['!turretselector'].onSelected.append(self.changeSpec)
        self.__app.widgets['!engineselector'].onSelected.append(self.changeSpec)
        self.__app.widgets['!radioselector'].onSelected.append(self.changeSpec)
        self.__app.widgets['!gunselector'].onSelected.append(self.changeSpec)
        self.__app.widgets['!shellselector'].onSelected.append(self.changeSpec)
        self.changeSpec()

    def createSelectorBars(self, master):
        selectors = []
        for row in self.__selectorsdesc:
            bar = tkinter.Frame(master)
            bar.pack(side='top', expand=1, fill='x', padx=4, pady=1)
            for desc in row:
                widget = SelectorPanel(bar, app=self.__app, desc=desc)
                widget.pack(side='left')
                selectors.append(widget)
        for widget in selectors:
            widget.setup()

    def changeSpec(self):
        ctx = self.getSelectedValues()
        result = self.__app.vd.getVehicleItems(g_data.keys(), ctx)
        for k, v in result.items():
            if v is None:
                v = ''
            g_data[k].set(v)

    def createDescriptionView(self, master):
        view = tkinter.Frame(master, highlightthickness=1, highlightbackground='gray')
        view.pack(side='top', expand=1, fill='x', padx=8, pady=4)
        opts = { 'label':{'width':8, 'anchor':'e'}, 'value':{'width':100, 'anchor':'w'} }
        self.__vehicleDescs = []
        for entry in self.__titlesdesc:
            panel = PanelItemValue(view, entry, self.getVehicleValue, option=opts)
            self.__vehicleDescs.append(panel)

    def createSpecView(self, master, desc, option):
        view = tkinter.Frame(master)
        view.pack(side='top', expand=1, fill='x')
        option = desc.get('guioption', {})
        for column in desc.get('columns', []):
            columnOption = column.get('guioption', option)
            columnView = tkinter.Frame(view)
            columnView.pack(side='left', anchor='n')
            for row in column.get('rows', []):
                rowOption = row.get('guioption', columnOption)
                rowView = tkinter.Frame(columnView, highlightthickness=1, highlightbackground='gray')
                rowView.pack(side='top', expand=1, padx=8, pady=2, anchor='w')
                for item in row.get('items', []):
                    itemOption = item.get('guioption', rowOption)
                    widget = SpecViewItem(rowView, desc=item, option=itemOption)
                    widget.pack(side='top')
        return

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
        if len(self.__app.widgets) == 0:
            return None
        param = {}
        param['nation'] = self.__app.widgets['!nationselector'].getId()
        param['vehicle'] = self.__app.widgets['!vehicleselector'].getId()
        param['chassis'] = self.__app.widgets['!chassisselector'].getId()
        param['turret'] = self.__app.widgets['!turretselector'].getId()
        param['engine'] = self.__app.widgets['!engineselector'].getId()
        param['radio'] = self.__app.widgets['!radioselector'].getId()
        param['gun'] = self.__app.widgets['!gunselector'].getId()
        param['shell'] = self.__app.widgets['!shellselector'].getId()
        return param
 

    def getVehicleValue(self, schema):
        app = self.__app
        tags = schema['value']
        if isinstance(tags, str):
            tags = [tags]
        form = schema.get('format', None)
        ctx = self.getSelectedValues()
        #print('schema={}, ctx={}'.format(schema, ctx))
        result = app.vd.getVehicleItems(tags, ctx)
        for k in tags:
            if schema.get('consider', None) == 'float':
                result[k] = float(result[k]) if result[k] is not None else ''
        result = [ result[k] for k in tags ]
        result = list(map(lambda x:x if x is not None else '', result))
        #print('tags={}, result={}'.format(tags, result))
        if form:
            try:
                text = form.format(*result)
            except ValueError:
                text = ''
        elif isinstance(result, list):
            text = ' ' .join(result)
        else:
            text = result
        #print('text={}'.format(text))
        return text

    def createMessage(self):
        param = self.getSelectedValues()
        values = self.__strage.getDescription(param)
        message = getOutputCsv(values)
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

