import functools
import io

from enum import Enum, auto
from collections import deque

VTYPES_LEN = 2
BYTE_ORDER = 'big'
INT_LEN_LEN = 1

class BinaryAuto(Enum):
    def _generate_next_value_(name, start, count, last_values):   
        return len(last_values).to_bytes(VTYPES_LEN, 'big')

class VALUE_TYPES(BinaryAuto):
    INT         = auto()
    FLOAT       = auto()
    BYTES       = auto()
    STR         = auto()
    NONE        = auto()
    LIST        = auto()
    TUPLE       = auto()
    ITER        = auto()
    SET         = auto()
    

@functools.singledispatch
def convert(arg):
    try:
        return arg.__convert__()
    except Exception:
        raise ValueError("Could not convert argument type %s" % type(arg))
            
@convert.register
def _(arg: int):
    byte_len = arg.bit_length() // 8 + 1
    
    bb = byte_len.to_bytes(INT_LEN_LEN, BYTE_ORDER)
    
    return VALUE_TYPES.INT.value + bb + arg.to_bytes(byte_len, BYTE_ORDER)

@convert.register
def _(arg: float):
    return VALUE_TYPES.FLOAT.value + convert(arg.as_integer_ratio())
        
@convert.register
def _(arg: str):
    b = arg.encode()
    return VALUE_TYPES.STR.value + convert(len(b)) + b
    
@convert.register
def _(arg: bytes):
    return VALUE_TYPES.BYTES.value + convert(len(arg)) + arg

@convert.register
def _(arg: list):
    collected = []
    for subarg in arg:
        collected.append(convert(subarg))
    
    return b"".join([VALUE_TYPES.LIST.value, convert(len(collected))] + collected)

@convert.register
def _(arg: tuple):
    collected = []
    for subarg in arg:
        collected.append(convert(subarg))
    
    return b"".join([VALUE_TYPES.TUPLE.value, convert(len(collected))] + collected)

@convert.register
def _(arg: set):
    collected = []
    for subarg in arg:
        collected.append(convert(subarg))
    
    return b"".join([VALUE_TYPES.SET.value, convert(len(collected))] + collected)

@convert.register(type(None))
def _(arg):
    return VALUE_TYPES.NONE.value

class ByteBuffer:
    def __init__(self, data=None):
        if data is not None:
            self.data = deque((data,))
        else:
            self.data = deque()
    
    def read(self, read_size):
        len_found = 0
        collected = []
        
        while len_found < read_size:
            d = self.data.pop()
            left = read_size - len_found
            len_found += len(d)
            if len(d) > left:
                collected.append(d[:left])
                self.data.append(d[left:])
            else:
                collected.append(d)
        
        return b"".join(collected)
    
    def write(self, data):
        self.data.appendleft(data)
    
    def has_values(self):
        return len(self.data) > 0 and any(map(lambda x: len(x)>0, self.data))


class Decoder:
    def __init__(self, data=b"", custom_byte_buffer=None):
        if custom_byte_buffer is None:
            self.io = ByteBuffer(data)
        else:
            self.io = custom_byte_buffer #Some methods may not work
    def feed(self, data):
        self.io.write(data)
    
    def get_value(self, ensure_type=None):
        tp = self.io.read(VTYPES_LEN)
        etp = VALUE_TYPES(tp)
        
        if ensure_type is not None:
            assert etp is ensure_type
        
        #print(etp)
        
        if etp is VALUE_TYPES.INT:
            bl = int.from_bytes(self.io.read(1), BYTE_ORDER)
            return int.from_bytes(self.io.read(bl), BYTE_ORDER)
        elif etp is VALUE_TYPES.FLOAT:
            v = self.get_value(ensure_type=VALUE_TYPES.TUPLE)
            return v[0] / v[1]
        elif etp is VALUE_TYPES.BYTES:
            ln = self.get_value(ensure_type=VALUE_TYPES.INT)
            return self.io.read(ln)
        elif etp is VALUE_TYPES.STR:
            ln = self.get_value(ensure_type=VALUE_TYPES.INT)
            return self.io.read(ln).decode()
        elif etp is VALUE_TYPES.ITER:
            ln = self.get_value(ensure_type=VALUE_TYPES.INT)
            return (self.get_value() for i in range(ln))
        elif etp is VALUE_TYPES.LIST:
            ln = self.get_value(ensure_type=VALUE_TYPES.INT)
            return [self.get_value() for i in range(ln)]
        elif etp is VALUE_TYPES.TUPLE:
            ln = self.get_value(ensure_type=VALUE_TYPES.INT)
            return tuple((self.get_value() for i in range(ln)))
        elif etp is VALUE_TYPES.SET:
            ln = self.get_value(ensure_type=VALUE_TYPES.INT)
            return set((self.get_value() for i in range(ln)))
        elif etp is VALUE_TYPES.NONE:
            return None
        else:
            raise ValueError("Wrong type byte")
        
            
    def has_values(self):
        return self.io.has_values()

if __name__ == "__main__":
    
    data = [1, 2, (3, 4, (1, 3, 5, 1.5, None)), [b"test", "test"]]
    
    conv = convert(data)
    
    d = Decoder(conv)
    
    print(conv)
    
    while d.has_values():
        v = d.get_value()
        print(v)
        print(v == data)
        
    
    
