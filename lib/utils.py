import io
import zipfile
from lib.XmlUnpacker import XmlUnpacker
from lib.config import g_config as config
    
def readXmlData(domain, target=None):
    xmlunpacker = XmlUnpacker()
    vpath = config.DATA[domain]['vpath'] + ('/' + target if target else '')

    if config.DATA[domain]['extracted']:
        path = '/'.join([ config.DATA[domain]['extracted'], vpath.split('/', 1)[1] ])
        try:
            with open(path, 'rb') as file:
                root = xmlunpacker.read(file)
        except:
            root = None
    else:
        pkgpath = '/'.join([ config.BASE_DIR, config.PKG_RELPATH, config.DATA[domain]['packed'] ])
        try:
            with zipfile.ZipFile(pkgpath, 'r') as zip:
                with zip.open(vpath, 'r') as data:
                    root = xmlunpacker.read(io.BytesIO(data.read()))
        except:
            root = None
    return root
