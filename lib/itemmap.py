
import re


class MapFactory(object):

    def __init__(self, app):
        self.app = app

    def create(self, desc):
        if desc is None:
            obj = MapNull(self.app, desc)
        elif isinstance(desc, dict):
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


class MapNull(MapMeta):
    def getValue(self, value):
        return value

class MapDict(MapMeta):
    def getValue(self, value):
        if value is None:
            return None
        result = value.split()
        result = list(filter(None, map(lambda x: self.desc.get(x, None), result)))
        if len(result) == 0:
            if '' in self.desc:
                result = self.desc['']
            else:
                result = None
        else:
            result = ' '.join(result)
        return result

class MapRoman(MapMeta):
    def getValue(self, value):
        if value is None:
            return None
        dict = self.app.resource.getValue('settings:tiersLabel')
        result = dict.get(value, None)
        return result

class MapGettext(MapMeta):
    def getValue(self, value):
        if self.app.gettext is None:
            raise AttributeError('translate engine is not prepared.')
        if value is None:
            return None
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
        if value is None:
            return None
        result = value.split()
        if self.pos is not None:
            result = result[self.pos]
        return result
