

import tkinter
import tkinter.ttk
import tkinter.font

from lib.wselector import TestSelector


class GuiApplication(tkinter.Frame):

    def __init__(self, master=None):
        super(GuiApplication, self).__init__(master)
        self.pack()
        selector = TestSelector(self)
        selector.pack()

if __name__ == '__main__':
    gui = GuiApplication()
    gui.mainloop()