import logging
import io
import zipfile
from lib.XmlUnpacker import XmlUnpacker

from lib.config import g_config as config

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

def readXmlData(domain, target=None):
    xmlunpacker = XmlUnpacker()
    try:
        stream = readData(domain, target)
    except:
        logger.warning('cannot open file: {}, {}'.format(domain, target))
        root = None
        return
    try:
        root = xmlunpacker.read(stream)
    except:
        stream.seek(0)
        data = [ d for d in stream.readlines() if b'xmlns:xmlref' not in d ]
        data = b''.join(data)
        try:
            root = xmlunpacker.read(io.BytesIO(data))
        except:
            logger.error('cannot parse file: {}, {}'.format(domain, target))
            root = None
            raise
    return root


def readData(domain, target=None):
    vpath = config.DATA[domain]['vpath'] + ('/' + target if target else '')

    if config.DATA[domain]['extracted']:
        path = '/'.join([ config.DATA[domain]['extracted'], vpath.split('/', 1)[1] ])
        try:
            with open(path, 'rb') as file:
                stream = io.BytesIO(file.read())
        except:
            logger.debug('cannot open file: {}'.format(path))
            raise
    else:
        pkgpath = '/'.join([ config.BASE_DIR, config.PKG_RELPATH, config.DATA[domain]['packed'] ])
        try:
            with zipfile.ZipFile(pkgpath, 'r') as zip:
                with zip.open(vpath, 'r') as data:
                    stream = io.BytesIO(data.read())
        except:
            logger.debug('cannot open vfile: {}, {}'.format(pkgpath, vpath))
            raise
    return stream
