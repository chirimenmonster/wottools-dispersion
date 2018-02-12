import gettext
from lib.config import g_config as config

class Translate(object):
    __gettext = {}
    
    def translate(self, text):   
        if text is None:
            return ''
        if not text[0] == '#':
            return text
        domain, name = text[1:].split(':')
        if domain not in self.__gettext:
            localedir = '/'.join([ config.BASE_DIR, config.LOCALE_RELPATH ])
            self.__gettext[domain] = gettext.translation(domain, languages=['text'], localedir=localedir, fallback=True)
        if isinstance(self.__gettext[domain], gettext.GNUTranslations):
            return self.__gettext[domain].gettext(name)
        return text

g_translate = Translate().translate
