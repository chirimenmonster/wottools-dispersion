
import tkinter.ttk


g_data = {}


class SpecViewItem(tkinter.Frame):
    def __init__(self, *args, desc=None, option={}, **kwargs):
        super(SpecViewItem, self).__init__(*args, **kwargs, borderwidth=0)
        label = desc.get('label', None)
        value = desc.get('value', None)
        unit = desc.get('unit', None)
        self.isPhantom = True if desc.get('attr', None) == 'phantom' else False
        g_data[value] = tkinter.StringVar(value='0')
        widget = LabelItem(self, text=label, **option['label'])
        widget.pack(side='left')
        
        widget = ValueItem(self, textvariable=g_data[value], **option['value'])
        widget.pack(side='left')
        g_data[value].trace('w', lambda *args, w=widget, n=value: w.callback(*args, name=n))

        widget = UnitItem(self, text=unit, **option['unit'])
        widget.pack(side='left')


class LabelItem(tkinter.Label):
    pass
    
class ValueItem(tkinter.Label):
    def callback(self, *args, name=None):
        print('{}, {}'.format(name, repr(g_data[name].get())))
        if g_data[name].get() == '':
            if self.master.isPhantom:
                self.master.pack_forget()
        else:
            self.master.pack()            
    
class UnitItem(tkinter.Label):
    pass
