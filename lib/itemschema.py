

class ItemSchema(object):

    def resolveResources(self):
        pass
        
    def resolveMap(self):
        pass

    def resolvSort(self):
        pass


class MapFactory(object):
    def create(self, desc):
        if isinstance(desc, dict):
            obj = MapDict(dict)

            
class MapMeta(object)
    def __init__(self, desc):
        self.desc = desc

    def getValue(self, value):
        raise NotImplementedError


class MapDict(MapMeta):
    def getValue(self, value):
        result = value.split()
        result = list(filter(None, map(lambda x: self.desc.get(x, None), result)))
        result = ' '.join(result)
        return result

class MapGettext(MapMeta):
    def getValue(self, value):
        if app.gettext is None:
            raise AttributeError('translate engine is not prepared.')
        result = app.gettext.translate(value)
        return result

class MapSplit(MapMeta):
    def __init__(self, desc):
        super(MapSplit, self).__init__(desc)
        match = re.fullmatch(r'split\(\)(\[(\d+)\])?', rule)
        if match is None:
            raise NotImplementedError('map rule: {}'.format(rule))
        if match.group(2) is not None:
            self.pos = int(match.group(2))
        else:
            self.pos = None

    def getValue(self, value):
        result = value.split()
        if self.pos is not None:
            result = result[self.pos]
        return result
