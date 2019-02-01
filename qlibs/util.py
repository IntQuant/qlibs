from weakref import WeakValueDictionary

def try_write(prog, at, data):
    """Tries to write data into member of moderngl program"""
    o = prog.get(at, default=None)
    if o is not None:
        o.write(data)


def weak_ref_cache(fun):
    cache = WeakValueDictionary()
    def _(*args, **kwargs):
        if args in cache:
            return cache[args]
        else:
            return fun(*args, **kwargs)
    return _
