import sys
import io
from lib.widgets import Application
from lib.strage import Strage
from lib.config import parseArgument

if __name__ == '__main__':
    import io, sys
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

    parseArgument()

    app = Application(strage=Strage())
    app.mainloop()
    
