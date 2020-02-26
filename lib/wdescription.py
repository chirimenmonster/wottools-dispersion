
import math
import string
from collections import namedtuple
import tkinter.ttk

from lib.stats import VehicleStats
from lib.utils import VStatsFormatter

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
            self.stats[k] = v.value if v is not None else ''
        self.updateDisplay()
    
    def updateDisplay(self):
        formatter = VStatsFormatter()
        for d in self.displays:
            args = [ self.stats[k] for k in d.tags ]
            if len(list(filter(lambda x: x is not None or x == '', args))) == 0:
                text = ''
            else:
                text = formatter.vformat(d.template, args, None)
            d.textvariable.set(text)


class SpecViewItem(tkinter.Frame):
    def __init__(self, *args, app=None, desc=None, option={}, **kwargs):
        super(SpecViewItem, self).__init__(*args, **kwargs, borderwidth=0)
        self.isPhantom = True if desc.get('attr', None) == 'phantom' else False
        
        label = desc.get('label', None)
        widget = LabelItem(self, text=label, **option['label'])
        widget.pack(side='left')

        value = desc.get('value', None)
        factory = ValueItemFactory(app)
        widget = factory.create(self, desc=desc, **option['value'])
        widget.pack(side='left', fill='x', expand=1)

        unit = desc.get('unit', None)
        if unit is not None:
            widget = UnitItem(self, text=unit, **option['unit'])
            widget.pack(side='left')

    def update(self, isNone=False):
        self.pack_forget()
        if isNone and self.isPhantom:
            return
        #self.pack(side='top', fill='x', expand=1)
        self.pack(side='top')


class LabelItem(tkinter.Label):
    pass

class UnitItem(tkinter.Label):
    pass


class ValueItemFactory(object):
    def __init__(self, app):
        self.app = app
        
    def create(self, *args, desc=None, **kwargs):
        if desc.get('attr', '') == 'multiline':
            if 'justify' in kwargs:
                del kwargs['justify']
            widget = ValueTextItem(*args, app=self.app, desc=desc, **kwargs)
        else:
            widget = ValueItem(*args, app=self.app, desc=desc, **kwargs)
        return widget


class ValueItem(tkinter.Entry):
    def __init__(self, *args, app=None, desc=None, **kwargs):
        super(ValueItem, self).__init__(*args, **kwargs)
        self.app = app
        template = desc.get('format', '{}')
        stringvar = tkinter.StringVar(value='')
        stringvar.trace('w', self.callback)
        self['textvariable'] = stringvar
        self.__stringvar = stringvar
        self.app.vehicleStatsPool.add(desc['value'], template, stringvar, self)
        self.__isSecret = True if 'vehicle:secret' in desc['value'] else False

    def callback(self, *args):
        text = self.__stringvar.get()
        self.master.update(isNone=(text == ''))
        #if self.__isSecret:
        #    print('update: "{}", {}'.format(text, (text == '')), flush=True)


class ValueTextItem(tkinter.Text):
    def __init__(self, *args, app=None, desc=None, **kwargs):
        super(ValueTextItem, self).__init__(*args, **kwargs, height=4)
        self.font = tkinter.font.Font(family='Arial', size=10, weight='normal')
        self.app = app
        template = '{}'
        stringvar = tkinter.StringVar(value='')
        stringvar.trace('w', self.callback)
        self.__stringvar = stringvar
        self.app.vehicleStatsPool.add(desc['value'], '{}', stringvar, self)
        self.delete('1.0', 'end')
        self['height'] = 1
        #self.lock = True
        #self['yscrollcommand'] = self.setScroll
        self.__nrows = tkinter.StringVar(value='')
        #self.__nrows.trace('w', self.delayResize)
        self.bind('<Map>', self.catchMap)
        self['yscrollcommand'] = self.dummyScrollCommand

    def catchMap(self, *args):
        print('catchMap: change height=1', flush=True)
        self.__nrows.set(value='')
        #self['height'] = 1
        #self.resizeHeight()
        
        
    def delayResize(self, *args):
        print('derayResize:', flush=True)
        self.after(5000, self.resizeHeight)
   
    
    def resizeHeight(self, *args):
        bwidth = self.font.measure('0' * int(float(self['width'])))
        width = 0
        nlines = 0
        for line in self.get('1.0', 'end-1c').split('\n'):
            width = max(width, self.font.measure(line))
            nlines += math.ceil(width / bwidth)
            print('width={}, bwidth={},  nlines={}'.format(width, bwidth, nlines))
        nrows = nlines
        #nrows = self.__nrows.get()
        #nrows = self.__needsRows
        print('resizeHeight: nrows={}'.format(repr((nrows))), flush=True)
        self['height'] = nrows
        #if nrows != '':
        #    print('resizeHeight: set height, nrows={}'.format(repr((nrows))), flush=True)
        #    self['height'] = nrows
        #else:
        #    print('resizeHeight: unknown nrows={}'.format(repr((nrows))), flush=True)
        #self['height'] = 1
        #self['yscrollcommand'] = None
        #self['height'] = self.__nrows

    def getDisplayHeight(self):
        self.__nrows.set('')
        self['height'] = 1
        print('getDisplayHeight', flush=True)

    def dummyScrollCommand(self, first, last):
        first, last = float(first), float(last)
        nrows = self['height'] / (last - first)
        self.__needsRows = nrows
        #current = self.__nrows.get()
        print('dummyScrollCommand: need={}, height={}, first={}, last={}'.format(nrows, self['height'], first, last), flush=True)
        #if current != '':
        #    return
        #self.__nrows.set(nrows)
        #print('dummyScrollCommand: need={}, current={}'.format(nrows, self['height']), flush=True)

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

    def callback(self, *args):
        text = self.__stringvar.get()
        print('callback: len={}, text={}...'.format(len(text), text[:16]), flush=True)
        self.delete('1.0', 'end')
        #self['height'] = 1
        #self.lock = False
        self.insert('1.0', text)
        #self.resize()
        self.master.update(isNone=(text == ''))
        #self.__nrows.set('')
        #self['height'] = 1
        #self.delayResize()
        #self.after(1000, lambda : self.yview_moveto(0.0))
        #self.after(2000, lambda : self.yview_moveto(1.0))
        #self.after(1000, lambda : self.resizeHeight())
        self.resizeHeight()
