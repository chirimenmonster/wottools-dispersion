
import string
from collections import namedtuple
import tkinter.ttk

from lib.stats import VehicleStats

VehicleDisplay = namedtuple('VehicleDisplay', 'tags template textvariable widget')


class VehicleStatsPool(object):
    def __init__(self, app):
        self.app = app
        self.stats = {}
        self.displays = []

    def add(self, tags, template, stringvar, widget):
        if isinstance(tags, list):
            tags = tuple(tags)
        else:
            tags = tuple([tags])
        self.displays.append(VehicleDisplay(tags, template, stringvar, widget))
        for t in tags:
            self.stats[t] = ''

    def get(self):
        return self.stats
    
    def fetchStats(self, ctx):
        tags = self.stats.keys()
        result = self.app.vd.getVehicleItems(tags, ctx)
        result = VehicleStats(result, schema=self.app.settings.schema)
        for k, v in result.items():
            if v is None:
                v = ''
            self.stats[k] = v.value
        self.updateDisplay()
    
    def updateDisplay(self):
        formatter = string.Formatter()
        for d in self.displays:
            text = ''
            n = len(list(filter(lambda x: self.stats[x] is not None, d.tags)))
            if n > 0:
                for i, f in enumerate(formatter.parse(d.template)):
                    literal_text, _, format_spec, _ = f
                    text += literal_text
                    if format_spec is None:
                        continue
                    value = self.stats[d.tags[i]]
                    if value is not None:
                        text += formatter.format_field(value, format_spec)
            if d.textvariable is not None:
                d.textvariable.set(text)
            elif isinstance(d.widget, tkinter.Text):
                d.widget.delete('1.0', 'end')
                d.widget['height'] = 1
                d.widget.lock = False
                d.widget.insert('1.0', text)
            else:
                raise NotImplementedError


class SpecViewItem(tkinter.Frame):
    def __init__(self, *args, app=None, desc=None, option={}, **kwargs):
        super(SpecViewItem, self).__init__(*args, **kwargs, borderwidth=0)
        label = desc.get('label', None)
        value = desc.get('value', None)
        unit = desc.get('unit', None)
        self.isPhantom = True if desc.get('attr', None) == 'phantom' else False
        
        widget = LabelItem(self, text=label, **option['label'])
        widget.pack(side='left')

        if desc.get('attr', None) == 'multiline':
            opt = option['value'].copy()
            if 'justify' in opt:
                del opt['justify']
            widget = ValueTextItem(self, app=app, **opt)
            widget.pack(side='left', fill='x', expand=1)
        else:
            opt = option['value'].copy()
            widget = ValueItem(self, app=app, **opt)
            widget.pack(side='left')
        widget.setValue(desc)

        if unit is not None:
            widget = UnitItem(self, text=unit, **option['unit'])
            widget.pack(side='left')

    def assignValue(self, value):
        if value is None:
            if self.isPhantom:
                self.pack_forget()
        else:
            self.pack()


class LabelItem(tkinter.Label):
    pass

class UnitItem(tkinter.Label):
    pass
    
class ValueItem(tkinter.Entry):
    def __init__(self, *args, app=None, **kwargs):
        super(ValueItem, self).__init__(*args, **kwargs)
        self.app = app

    def setValue(self, desc):
        value = desc['value']
        template = desc.get('format', '{}')
        stringvar = tkinter.StringVar(value='')
        stringvar.trace('w', self.callback)
        self['textvariable'] = stringvar
        self.__stringvar = stringvar
        self.app.vehicleStatsPool.add(value, template, stringvar, self)

    def callback(self, *args):
        value = self.__stringvar.get()
        if value == '':
            value = None
        self.master.assignValue(value)


class ValueTextItem(tkinter.Text):
    def __init__(self, *args, app=None, **kwargs):
        super(ValueTextItem, self).__init__(*args, **kwargs, height=4)
        self.app = app
        self.delete('1.0', 'end')
        self.lock = True
        self['yscrollcommand'] = self.setScroll

    def setValue(self, desc):
        value = desc['value']
        self.app.vehicleStatsPool.add(value, '{}', None, self)

    def setScroll(self, first, last):
        if self.lock:
            return
        first, last = float(first), float(last)
        if first == 0.0 and last == 1.0:
            return
        nrows = self['height'] / (last - first)
        if nrows > 8:
            return
        self.lock = True
        self['height'] = nrows

