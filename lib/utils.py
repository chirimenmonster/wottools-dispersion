
import string


def substitute(value, ctx):
    if ctx is None:
        return value
    if isinstance(value, list):
        value = list(map(lambda x,c=ctx:self.substitute(x, c), value))
    elif isinstance(value, str):
        for p in list(string.Formatter().parse(value)):
            k = p[1]
            if k is not None:
                if k not in ctx:
                    raise KeyError('no key "{}" in ctx={}'.format(k, ctx))
                elif ctx[k] is None:
                    return None
        try:
            value = value.format(**ctx)
        except KeyError as e:
            raise KeyError(e, value, ctx) from e
        except TypeError as e:
            raise TypeError(e.args[0], value, ctx) from e
    return value
