"""
  Module for different random things
"""

from weakref import WeakValueDictionary

def try_write(prog, at, data):
    """Tries to write data into member of moderngl program"""
    o = prog.get(at, default=None)
    if o is not None:
        o.write(data)


def weak_ref_cache(fun):
    """Function decorator that caches output using wekrefs"""
    
    cache = WeakValueDictionary()
    def _(arg, *args, **kwargs):
        if arg in cache:
            return cache[arg]
        else:
            return fun(arg, *args, **kwargs)
    return _
