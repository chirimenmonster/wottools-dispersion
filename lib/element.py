
class Element(object):

    def __init__(self, value=None, schema=None):
        self.set(value, schema)

    def set(self, value, schema):
        self.__orig = value
        self.__schema = schema
        self.__type = schema.get('value', 'str')
        self.__value = None
        self.__str = None
        
    def __getValue(self):
        if self.__orig is None:
            return None
        type = self.__type
        if type == 'int':
            value = int(self.__orig)
        elif type == 'float':
            value = float(self.__orig)
        elif type == 'str':
            value = str(self.__orig)
        else:
            raise NotImplementedError
        self.__value = value
        return self.__value

    def __getStr(self):
        if self.__orig is None:
            return None
        self.__str = str(self.__orig)
        return self.__str
        
    def __lt__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError
        if self.__type != other.__type:
            raise TypeError('not same type, {} and {}'.format(self, other))
        return self.value.__lt__(other.value)

    @property
    def orig(self):
        return self.__orig

    @property
    def value(self):
        if self.__value is None:
            self.__value = self.__getValue()
        return self.__value

    @property
    def str(self):
        if self.__str is None:
            self.__str = self.__getStr()
        return self.__str

    @property
    def strlen(self):
        return len(self.__str)

    def getFormattedString(self, default='', width=None):
        if self.value is None:
            result = default
        elif 'format' in self.__schema:
            template = '{{:{}}}'.format(self.__schema['format'])
            result = template.format(self.value)
        else:
            result = self.str
        if width is not None:
            if self.__type in ('int', 'float'):
                result = result.rjust(width)
            else:
                result = result.ljust(width)
        return result

