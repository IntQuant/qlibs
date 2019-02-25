"""
  Module for different random things
"""

from weakref import WeakValueDictionary
from collections import Hashable


def try_write(prog, at, data):
    """Tries to write data into member of moderngl program"""
    o = prog.get(at, default=None)
    if o is not None:
        o.write(data)


def weak_ref_cache(fun):
    """Function decorator that caches output using wekrefs"""

    cache = WeakValueDictionary()

    def _(*args, **kwargs):
        margs = []
        for arg in args:
            if isinstance(arg, Hashable):
                margs.append(arg)
            else:
                margs.append(id(arg))

        margs = tuple(margs)

        if margs in cache:
            return cache[margs]
        else:
            res = fun(*args, **kwargs)
            cache[margs] = res
            return res

    return _


def dict_cache(fun):
    """Function decorator that caches output"""
    cache = dict()
    def _(*args, **kwargs):
        margs = []
        for arg in args:
            if isinstance(arg, Hashable):
                margs.append(arg)
            else:
                margs.append(id(arg))
        margs = tuple(margs)
        if margs in cache:
            return cache[margs]
        else:
            res = fun(*args, **kwargs)
            cache[margs] = res
            return res
    _.cache = cache
    return _
