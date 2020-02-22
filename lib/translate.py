
import gettext


class Gettext(object):

    def __init__(self, localedir=None):
        self.__localedir = localedir
        self.__translation = {}

    @property
    def localedir(self):
        return self.__localedir

    @localedir.setter
    def localedir(self, dir):
        self.__localedir = dir

    def getTranslation(self, domain):
        key = (self.__localedir, domain)
        if key in self.__translation:
            return self.__translation[key]
        translation = gettext.translation(domain, localedir=self.__localedir, languages=['text'], fallback=True)
        self.__translation[key] = translation
        return translation

    def translate(self, text):
        if text is None or not text[0] == '#':
            return text
        domain, name = text[1:].split(':')
        translation = self.getTranslation(domain)
        if isinstance(translation, gettext.GNUTranslations):
            text = translation.gettext(name)
        return text

