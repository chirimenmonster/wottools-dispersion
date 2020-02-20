
import re

from lib.utils import substitute


class ResourceFactory(object):

    def __init__(self, app):
        self.app = app

    def create(self, desc):
        if 'file' in desc and 'xpath' in desc:
            obj = ResourceXml(self.app, desc)
        elif 'immediate' in desc:
            obj = ResourceImmediate(self.app, desc)
        elif 'func' in desc:
            obj = ResourceFunction(self.app, desc)
        else:
            NotImplementedError('bad resource description, {}'.format(desc))
        return obj


class ResourceMeta(object):

    def __init__(self, app, desc):
        self.app = app
        self.desc = desc

    def getValue(self, ctx=None):
        raise NotImplementedError


class ResourceXml(ResourceMeta):

    def __init__(self, app, desc):
        super(ResourceXml, self).__init__(app, desc)
        self.file = desc['file']
        self.xpath = desc['xpath']
        self.param = desc.get('param', None)

    def getValue(self, ctx=None):
        if ctx is None:
            ctx = {}
        if self.param is not None:
            newctx = ctx.copy()
            for tag, rtag in self.param.items():
                newctx[tag] = self.app.resource.getRefValue(rtag, ctx)
            ctx = newctx
        file = substitute(self.file, ctx)
        xpath = substitute(self.xpath, ctx)
        if file is None or xpath is None:
            return None
        path = self.app.resource.vpath.getPathInfo(file)
        try:
            root = self.app.resource.strage.readXml(path)
        except FileNotFoundError or KeyError:
            result = None
        result = self.resolveXPath(root, xpath)
        return result

    def findNodes(self, root, xpath):
        nodeset = root.findall(xpath)
        nodeset = list(filter(lambda x:x.tag != 'xmlns:xmlref', nodeset))
        return nodeset

    def resolveXPath(self, root, xpath):
        match = re.fullmatch(r'([^()]*)\((.*)\)', xpath)
        if match:
            fname = match.group(1)
            xpath = match.group(2)
            if fname == 'name':
                result = self.findNodes(root, xpath)
                result = [ r.tag for r in result ]
            elif fname == 'position':
                submatch = re.fullmatch(r'(.*/)([^/]+)', xpath)
                if submatch:
                    xpath = submatch.group(1) + '*'
                    nname = submatch.group(2)
                else:
                    xpath, nname = '*', xpath
                result = self.findNodes(root, xpath)
                result = [ r.tag for r in result ]
                try:
                    result = [ result.index(nname) + 1 ]
                except:
                    print('xpath={}, nname={}'.format(xpath, nname))
                    raise
            else:
                raise NotImplementedError('unknown function: {}, xpath={}'.format(fname, xpath))
        else:
            result = self.findNodes(root, xpath)
            result = [ r.text for r in result ]
        return result


class ResourceImmediate(ResourceMeta):

    def __init__(self, app, desc):
        super(ResourceImmediate, self).__init__(app, desc)
        self.immediate = desc['immediate']

    def getValue(self, ctx=None):
        result = substitute(self.immediate, ctx)
        return result


class ResourceFunction(ResourceMeta):

    def __init__(self, app, desc):
        super(ResourceFunction, self).__init__(app, desc)
        table = { 'sum':FunctionSum, 'div':FunctionDiv, 'mul':FunctionMul,
            'join':FunctionJoin, 'or':FunctionOr, 'format':FunctionFormat }
        match = re.fullmatch(r'(.*)\((.*)\)', desc['func'])
        if match is None or match.group(1) is None:
            raise ValueError('func: {}'.format(desc['func']))
        self.func = match.group(1)
        self.arg0 = match.group(2)
        self.args = desc['args']
        self.param = desc.get('param', None)
        if self.func not in table:
            raise NotImplementedError('func: {}'.format(self.func))
        self.function = table[self.func](app, self.arg0, self.args)

    def getValue(self, ctx=None):
        result = self.function.getValue(ctx=ctx)
        return result


class FunctionMeta(object):

    def __init__(self, app, arg0, args):
        self.app = app
        self.arg0 = arg0
        self.args = args

    def _extractArg(self, arg, ctx=None):
        if ctx is not None and arg in ctx:
            return ctx[arg]
        else:
            return self.app.resource.getRefValue(arg, ctx)    

    def getArgs(self, ctx=None):
        return list(map(lambda x: self._extractArg(x, ctx), self.args))

    def getValue(self, ctx=None):
        raise NotImplementedError


class FunctionSum(FunctionMeta):
    def getValue(self, ctx=None):
        args = self.getArgs(ctx)
        if None in args:
            return None
        args = map(float, args)
        result = sum(args)
        return result

class FunctionDiv(FunctionMeta):
    def getValue(self, ctx=None):
        args = self.getArgs(ctx)
        args = list(map(float, args))
        result = args.pop(0)
        for a in args:
            result /= a
        return result

class FunctionMul(FunctionMeta):
    def getValue(self, ctx=None):
        args = self.getArgs(ctx)
        args = list(map(float, args))
        result = 1.0
        for a in args:
            result *= a
        return result

class FunctionJoin(FunctionMeta):
    def getValue(self, ctx=None):
        args = self.getArgs(ctx)
        result = []
        for a in args:
            if isinstance(a, list):
                result.extend(a)
            else:
                result.append(a)
        return result

class FunctionOr(FunctionMeta):
    def getValue(self, ctx=None):
        args = self.getArgs(ctx)
        result = None
        for a in args:
            result = result or a
        return result

class FunctionFormat(FunctionMeta):
    def getValue(self, ctx=None):
        match = re.fullmatch(r'\'(.*)\'', self.arg0)
        if match is None or match.group(1) is None:
            ValueError('arg={}'.format(self.args0))
        form = match.group(1)
        args = self.getArgs(ctx)
        result = form.format(*args)
        return result
