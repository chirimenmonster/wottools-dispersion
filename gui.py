
import sys
import io

from lib.config import parseArgument
from lib.application import Application
from lib.widgets import GuiApplication
from lib.dropdownlist import DropdownList


if __name__ == '__main__':
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    config = parseArgument(mode='gui')

    app = Application()
    app.setup(config)
    app.dropdownlist = DropdownList(app)

    gui = GuiApplication(app)
    gui.mainloop()
    
