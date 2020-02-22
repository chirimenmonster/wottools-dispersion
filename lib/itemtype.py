
import re


class TypeFactory(object):

    def __init__(self, app):
        self.app = app

    def create(self, desc):
        if desc is None:
            obj = TypeDefault(self.app, desc)
        elif desc == 'text':
            obj = TypeText(self.app, desc)
        elif desc == 'float':
            obj = TypeFloat(self.app, desc)
        elif desc == 'int':
            obj = TypeInt(self.app, desc)
        elif desc in ('list', 'dict'):
            obj = TypeOrig(self.app, desc)
        else:
            raise NotImplementedError('type rule: {}'.format(desc))
        return obj

            
class TypeMeta(object):
    def __init__(self, app, desc):
        self.app = app
        self.desc = desc

    def getValue(self, value):
        raise NotImplementedError

    def isNone(self, value):
        if value is None:
            return True
        if isinstance(value, list) and len(value) == 0:
            return True
        if isinstance(value, dict) and len(value) == 0:
            return True
        return False


class TypeOrig(TypeMeta):
    def getValue(self, value):
        return value

class TypeDefault(TypeMeta):
    def getValue(self, value):
        if self.isNone(value):
            return None
        if isinstance(value, list):
            if len(value) == 1:
                value = value[0]
            else:
                value = ' '.join(map(str, value))
        return value

class TypeText(TypeMeta):
    def getValue(self, value):
        if self.isNone(value):
            return None
        if isinstance(value, list):
            value = ' '.join(map(str, value))
        return value

class TypeNumber(TypeMeta):
    def __init__(self, app, desc):
        super(TypeNumber, self).__init__(app, desc)
        self.func = None

    def getValue(self, value):
        if self.isNone(value):
            return None
        if isinstance(value, list):
            if len(value) == 1:
                value = value[0]
            else:
                raise ValueError('data type "float" or "int" must one value: {}'.format(value))
        if self.func is None:
            raise NotImplementedError
        try:
            if isinstance(value, str):
                _ = list(map(self.func, value.split()))
        except ValueError as e:
            raise ValueError('data type mismatch, type="{}", value="{}"'.format(self.desc, value)) from e
        return value

class TypeInt(TypeNumber):
    def __init__(self, app, desc):
        super(TypeInt, self).__init__(app, desc)
        self.func = int

class TypeFloat(TypeNumber):
    def __init__(self, app, desc):
        super(TypeFloat, self).__init__(app, desc)
        self.func = float
