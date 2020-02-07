import sys
import io

from lib.widgets2 import Application
from lib.config import parseArgument, g_config as config
from lib.application import g_application as appenv

if __name__ == '__main__':
    import io, sys
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    parseArgument()

    config.GUI_DIR = 'test/data/res'
    config.scriptspkg = 'test/data/res/packages/scripts.pkg'
    config.schema = 'test/data/itemschema.json'
    config.localedir = 'test/data/res'
    appenv.setup(config)

    app = Application()
    app.mainloop()
    
