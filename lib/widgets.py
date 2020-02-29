
import tkinter
import tkinter.font

from lib.output import getOutputCsv
from lib.wselector import SelectorPanel
from lib.wdescription import SpecViewItem, VehicleStatsPool


class GuiApplication(tkinter.Frame):

    vehicleSpecSelectors = {
        'nation':   '!nationselector',
        'tier':     '!tierselector',
        'type':     '!vtypeselector',
        'secret':   '!secretselector'
    }
    vehicleSelectors = {
        'vehicle':  '!vehicleselector',
        'siege':    '!siegeselector'
    }
    moduleSelectors = {
        'chassis':  '!chassisselector',
        'turret':   '!turretselector',
        'engine':   '!engineselector',
        'radio':    '!radioselector',
        'gun':      '!gunselector',
        'shell':    '!shellselector'
    }
    allSelectors = {}
    allSelectors.update(vehicleSpecSelectors)
    allSelectors.update(vehicleSelectors)
    allSelectors.update(moduleSelectors)

    def __init__(self, app, master=None):
        super(GuiApplication, self).__init__(master)
        self.app = app
        self.app.vehicleStatsPool = VehicleStatsPool(app)
        self.app.widgets = {}
        self.specViewWidgets = []

        self.__itemgroup = app.settings.guiitems
        self.__titlesdesc = app.settings.guititles
        self.__selectorsdesc = app.settings.guiselectors

        font = tkinter.font.Font(family='Arial', size=10, weight='normal')
        self.app.font = font
        self.option_add('*font', font)
        self.option_add('*background', 'white')
        self.option_add('*relief', 'flat')
        self.master.title('Vehicle Selector')
        self.master.config(background='white', relief='flat')
        self.master.resizable(width=False, height=False)

        self.createSelectorBars(self.master)
        self.createDescriptionView(self.master)
        self.createSpecView(self.master, self.__itemgroup, None)
        self.createCommandView(self.master)

        if app.config.vehicle is not None:
            ctx = app.vd.getCtx(app.config.vehicle)
            ctx['siege'] = ''
            for k, w in self.vehicleSpecSelectors.items():
                self.app.widgets[w].selectId(ctx[k])
            for k, w in self.vehicleSelectors.items():
                self.app.widgets[w].updateTable()
                self.app.widgets[w].selectId(ctx[k])
            for w in self.moduleSelectors.values():
                self.app.widgets[w].updateTable()

        for w in list(self.vehicleSelectors.values()) + list(self.moduleSelectors.values()):
            self.app.widgets[w].onSelected.append(self.changeSpec)
        
        self.changeSpec()

    def createSelectorBars(self, master):
        selectors = []
        for row in self.__selectorsdesc:
            bar = tkinter.Frame(master)
            bar.pack(side='top', expand=1, fill='x', padx=4, pady=1)
            for desc in row:
                widget = SelectorPanel(bar, app=self.app, desc=desc)
                widget.pack(side='left')
                selectors.append(widget)
        for widget in selectors:
            widget.setup()

    def createDescriptionView(self, master):
        view = tkinter.Frame(master, highlightthickness=1, highlightbackground='gray')
        view.pack(side='top', expand=1, fill='x', padx=8, pady=4)
        opts = { 'label':{'width':8, 'anchor':'e'}, 'value':{'width':116} }
        self.__vehicleDescs = []
        for entry in self.__titlesdesc:
            widget = SpecViewItem(view, app=self.app, desc=entry, option=opts)
            widget.pack(side='top', fill='x', expand=1)

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
                    widget = SpecViewItem(rowView, app=self.app, desc=item, option=itemOption)
                    self.specViewWidgets.append(widget)

    def createCommandView(self, master):
        label = 'copy to clipboard'
        option = {'relief':'ridge', 'borderwidth':2}
        copyButton = tkinter.Button(master, text=label, command=self.createMessage, **option)
        copyButton.pack(side='top', expand=1, fill='x', padx=7, pady=2)   

    def changeSpec(self):
        ctx = self.getSelectedValues()
        self.app.vehicleStatsPool.fetchStats(ctx)
        #print(self.app.vehicleStatsPool.get(), flush=True)

    def getSelectedValues(self):
        if len(self.app.widgets) == 0:
            return None
        ctx = {}
        for k in ('nation', 'vehicle', 'siege', 'chassis', 'turret', 'engine', 'radio', 'gun', 'shell'):
            w = self.allSelectors[k]
            ctx[k] = self.app.widgets[w].getId()
        return ctx
 
    def createMessage(self):
        result = self.app.vehicleStatsPool.get()
        message = getOutputCsv(result)
        self.master.clipboard_clear()
        self.master.clipboard_append(message)
