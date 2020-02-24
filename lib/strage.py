
import io
import re
import zipfile
import xml.etree.ElementTree as ET
import logging
import traceback

from lib.XmlUnpacker import XmlUnpacker
from lib.vpath import PathInfo

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Strage(object):

    def __init__(self):
        self.__cachedData = {}
        self.__cachedXml = {}
        self.__cachedZip = {}

    def readStream(self, path, pkg=None):
        if not isinstance(path, PathInfo):
            path, file = PathInfo(path, pkg), path
        else:
            file, pkg = path
        if pkg:
            if pkg in self.__cachedZip:
                zip = self.__cachedZip[pkg]
            else:
                try:
                    zip = zipfile.ZipFile(pkg, 'r')
                except FileNotFoundError:
                    raise FileNotFoundError('pkgfile not found: {}'.format(pkg))
                self.__cachedZip[pkg] = zip
            try:
                with zip.open(file, 'r') as fp:
                    stream = io.BytesIO(fp.read())
            except KeyError as e:
                raise KeyError('file not found: {}, in pkgfile: {}'.format(file, pkg)) from e
        else:
            try:
                with open(file, 'rb') as fp:
                    stream = io.BytesIO(fp.read())
            except FileNotFoundError:
                raise FileNotFoundError('cannot open file: {}'.format(file))
        return stream

    def readData(self, path, pkg=None):
        if not isinstance(path, PathInfo):
            path, file = PathInfo(path, pkg), path
        if path in self.__cachedData:
            return self.__cachedData[path]
        data = self.readStream(path).read()
        self.__cachedData[path] = data
        return data

    def readXml(self, path, pkg=None):
        if not isinstance(path, PathInfo):
            path, file = PathInfo(path, pkg), path
        if path in self.__cachedXml:
            return self.__cachedXml[path]
        xmlunpacker = XmlUnpacker()
        stream = self.readStream(path)
        try:
            root = xmlunpacker.read(stream)
        except ET.ParseError:
            stream.seek(0)
            data = stream.read()
            data = re.sub(r'<xmlns:xmlref>.*?</xmlns:xmlref>', '', data.decode('utf-8')).encode('utf-8')
            try:
                root = xmlunpacker.read(io.BytesIO(data))
            except:
                logger.error('cannot parse file: {}'.format(path))
                raise
        self.__cachedXml[path] = root
        return root

    def isCachedData(self, path, pkg=None):
        if not isinstance(path, PathInfo):
            path = PathInfo(path, pkg)
        return path in self.__cachedData

    def isCachedXml(self, path, pkg=None):
        if not isinstance(path, PathInfo):
            path = PathInfo(path, pkg)
        return path in self.__cachedXml
