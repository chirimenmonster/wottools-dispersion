from functools import partial

import tkinter
import tkinter.ttk
import tkinter.font

from lib.output import getOutputCsv
from lib.stats import VehicleStats
from lib.wselector import SelectorPanel
from lib.wdescription import SpecViewItem, updateDisplayValue, g_vehicleStats


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

    def createDescriptionView(self, master):
        view = tkinter.Frame(master, highlightthickness=1, highlightbackground='gray')
        view.pack(side='top', expand=1, fill='x', padx=8, pady=4)
        opts = { 'label':{'width':8, 'anchor':'e'}, 'value':{'width':100, 'anchor':'w'} }
        self.__vehicleDescs = []
        for entry in self.__titlesdesc:
            widget = SpecViewItem(view, desc=entry, option=opts)
            widget.pack(side='top')

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

    def changeSpec(self):
        ctx = self.getSelectedValues()
        tags = g_vehicleStats.keys()
        result = self.__app.vd.getVehicleItems(g_vehicleStats.keys(), ctx)
        result = VehicleStats(result, schema=self.__app.settings.schema)
        for k, v in result.items():
            if v is None:
                v = ''
            g_vehicleStats[k] = v.value
        updateDisplayValue()

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
 

    def createMessage(self):
        message = getOutputCsv(g_vehicleStats)
        self.master.clipboard_clear()
        self.master.clipboard_append(message)
