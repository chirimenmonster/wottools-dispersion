
import sys
import io
import os

from lib.widgets import Application
from lib.config import parseArgument, g_config as config
from lib.application import g_application as appenv
from lib.dropdownlist import DropdownList


if __name__ == '__main__':
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


    config.schema = 'res/itemschema.json'
    config.gui = True

    parseArgument()

    appenv.setup(config)
    appenv.dropdownlist = DropdownList(appenv)

    app = Application()
    app.mainloop()
    
