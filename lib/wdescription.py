
from collections import namedtuple
import tkinter.ttk

VehicleDisplay = namedtuple('VehicleDisplay', 'tags template textvariable')

g_vehicleStats = {}
g_vehicleDisplays = []


def updateDisplayValue():
    for d in g_vehicleDisplays:
        values = [ g_vehicleStats[k] for k in d.tags ]
        if None in values:
            text = ''
        else:
            try:
                text = d.template.format(*values)
            except:
                print(d.tags, d.template, repr(values))
                raise
        d.textvariable.set(text)


class SpecViewItem(tkinter.Frame):
    def __init__(self, *args, desc=None, option={}, **kwargs):
        super(SpecViewItem, self).__init__(*args, **kwargs, borderwidth=0)
        label = desc.get('label', None)
        value = desc.get('value', None)
        unit = desc.get('unit', None)
        self.isPhantom = True if desc.get('attr', None) == 'phantom' else False
        
        widget = LabelItem(self, text=label, **option['label'])
        widget.pack(side='left')
        
        widget = ValueItem(self, **option['value'])
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

    
class ValueItem(tkinter.Label):
    def setValue(self, desc):
        value = desc['value']
        if isinstance(value, list):
            tags = tuple(value)
        else:
            tags = tuple([value])
        template = desc.get('format', '{}')
        stringvar = tkinter.StringVar(value='')
        stringvar.trace('w', self.callback)
        self['textvariable'] = stringvar
        self.__stringvar = stringvar
        g_vehicleDisplays.append(VehicleDisplay(tags, template, stringvar))
        for t in tags:
            g_vehicleStats[t] = ''

    def callback(self, *args):
        value = self.__stringvar.get()
        if value == '':
            value = None
        self.master.assignValue(value)


class UnitItem(tkinter.Label):
    pass
