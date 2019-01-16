def try_write(prog, at, data):
    """Tries to write data into member of moderngl program"""
    o = prog.get(at, default=None)
    if o is not None:
        o.write(data)
