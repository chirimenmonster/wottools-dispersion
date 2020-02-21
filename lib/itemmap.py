
import re


class MapFactory(object):

    def __init__(self, app):
        self.app = app

    def create(self, desc):
        if isinstance(desc, dict):
            obj = MapDict(self.app, desc)
        elif desc == 'roman()':
            obj = MapRoman(self.app, desc)
        elif desc == 'gettext()':
            obj = MapGettext(self.app, desc)
        elif desc.startswith('split()'):
            obj = MapSplit(self.app, desc)
        else:
            raise NotImplementedError('map rule: {}'.format(desc))
        return obj

            
class MapMeta(object):
    def __init__(self, app, desc):
        self.app = app
        self.desc = desc

    def getValue(self, value):
        raise NotImplementedError


class MapDict(MapMeta):
    def getValue(self, value):
        result = value.split()
        result = list(filter(None, map(lambda x: self.desc.get(x, None), result)))
        result = ' '.join(result)
        return result

class MapRoman(MapMeta):
    def getValue(self, value):
        dict = self.app.resource.getValue('settings:tiersLabel')
        result = dict.get(value, None)
        return result

class MapGettext(MapMeta):
    def getValue(self, value):
        if self.app.gettext is None:
            raise AttributeError('translate engine is not prepared.')
        result = self.app.gettext.translate(value)
        return result

class MapSplit(MapMeta):
    def __init__(self, app, desc):
        super(MapSplit, self).__init__(app, desc)
        match = re.fullmatch(r'split\(\)(\[(\d+)\])?', desc)
        if match is None:
            raise NotImplementedError('map rule: {}'.format(desc))
        if match.group(2) is not None:
            self.pos = int(match.group(2))
        else:
            self.pos = None

    def getValue(self, value):
        result = value.split()
        if self.pos is not None:
            result = result[self.pos]
        return result
