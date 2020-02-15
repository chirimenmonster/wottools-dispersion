
class Element(object):

    def __init__(self, value=None, schema=None, orderType=None):
        if isinstance(value, Element):
            if schema is not None or resource is not None:
                raise NotImplementedError
            other = value
            value = other.orig
            schema = other.schema
            orderType = other.orderType
        self.set(value, schema, orderType)

    def set(self, value, schema, orderType):
        self.__orig = value
        self.__schema = schema
        self.__orderType = orderType
        self.__type = schema.get('value', 'str')
        self.__value = None
        self.__str = None
        self.__order = None
        
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

    def __getOrder(self):
        type = self.__schema.get('sort', None)
        if type is None:
            pass
        elif type in self.orderType:
            order = self.orderType[type]
            return order.index(self.value)
        else:
            raise NotImplementedError('unknwon sort type: {}'.format(type))
        return self.value

    def __assertType(self, other):
        if not isinstance(other, type(self)):
            raise TypeError
        if self.__type != other.__type:
            raise TypeError('not same type, {} and {}'.format(self, other))    
        
    def __lt2__(self, other, reverse=False):
        self.__assertType(other)
        if self.order is None:
            if other.order is None:
                return False
            return True
        if reverse:
            if self.order.__eq__(other.order):
                return False
            elif self.order.__lt__(other.order):
                return False
            return True
        return self.order.__lt__(other.order)

    @property
    def orig(self):
        return self.__orig

    @property
    def schema(self):
        return self.__schema

    @property
    def resource(self):
        return self.__resource

    @property
    def orderType(self):
        return self.__orderType

    @property
    def value(self):
        if self.__value is None:
            self.__value = self.__getValue()
        return self.__value

    @property
    def order(self):
        if self.__order is None:
            self.__order = self.__getOrder()
        return self.__order

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

