#Need to make something better

import functools
import io

from enum import Enum, auto
from collections import deque
from ..collections import ByteBuffer

VTYPES_LEN = 1
BYTE_ORDER = 'big'
INT_LEN_LEN = 1

class BinaryAuto(Enum):
    def _generate_next_value_(name, start, count, last_values):   
        return len(last_values).to_bytes(VTYPES_LEN, 'big')

class VALUE_TYPES(BinaryAuto):
    INT         = auto()
    #TODO: add miniint
    FLOAT       = auto()
    BYTES       = auto()
    STR         = auto()
    NONE        = auto()
    LIST        = auto()
    TUPLE       = auto()
    SET         = auto()
    CUSTOM      = auto()

class SECONDARY_INT_PARAMS(BinaryAuto):
    POSITIVE    = auto()
    NEGATIVE    = auto()
    LP_INT      = auto() #TODO
    LN_INT      = auto() #TODO

class ConvertionLookup():
    def __init__(self):
        self.obj_to_id = dict()
        self.id_to_obj = dict()
    
    def register(self, obj: type, _id):
        assert obj not in self.obj_to_id
        self.obj_to_id[obj] = _id
        self.id_to_obj[_id] = obj

conv_lookup = ConvertionLookup()

def make_qlibs_obj_id(shift):
    return 1000 + shift

@functools.singledispatch
def convert(arg):
    try:
        obj_id = conv_lookup.obj_to_id[type(arg)]
        data = arg.__convert__()
        return VALUE_TYPES.CUSTOM.value + convert(obj_id) + convert(len(data)) + data
    except Exception:
        raise ValueError("Could not convert argument type %s" % type(arg))
            
@convert.register
def _(arg: int):
    byte_len = abs(arg.bit_length()) // 8 + 1
    
    bb = byte_len.to_bytes(INT_LEN_LEN, BYTE_ORDER)
    
    if arg >= 0:
        return VALUE_TYPES.INT.value + SECONDARY_INT_PARAMS.POSITIVE.value + bb + arg.to_bytes(byte_len, BYTE_ORDER)
    else:
        return VALUE_TYPES.INT.value + SECONDARY_INT_PARAMS.NEGATIVE.value + bb + abs(arg).to_bytes(byte_len, BYTE_ORDER)
        
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


class Decoder:
    def __init__(self, data=b"", custom_byte_buffer=None):
        if custom_byte_buffer is None:
            self.io = ByteBuffer(data)
        else:
            self.io = custom_byte_buffer #Some methods may not work
        self.conv_lookup = conv_lookup
    
    def feed(self, data):
        self.io.write(data)
    
    def get_value(self, ensure_type=None):
        tp = self.io.read(VTYPES_LEN)
        etp = VALUE_TYPES(tp)
        
        if ensure_type is not None:
            assert etp is ensure_type
    
        #int
        if etp is VALUE_TYPES.INT:
            sign = SECONDARY_INT_PARAMS(self.io.read(VTYPES_LEN))
            bl = int.from_bytes(self.io.read(1), BYTE_ORDER)
            value = int.from_bytes(self.io.read(bl), BYTE_ORDER)
            if sign is SECONDARY_INT_PARAMS.POSITIVE:
                return value
            elif sign is SECONDARY_INT_PARAMS.NEGATIVE:
                return -value
        #float
        elif etp is VALUE_TYPES.FLOAT:
            v = self.get_value(ensure_type=VALUE_TYPES.TUPLE)
            return v[0] / v[1]
        #bytes
        elif etp is VALUE_TYPES.BYTES:
            ln = self.get_value(ensure_type=VALUE_TYPES.INT)
            return self.io.read(ln)
        #str
        elif etp is VALUE_TYPES.STR:
            ln = self.get_value(ensure_type=VALUE_TYPES.INT)
            return self.io.read(ln).decode()
        #list
        elif etp is VALUE_TYPES.LIST:
            ln = self.get_value(ensure_type=VALUE_TYPES.INT)
            return [self.get_value() for i in range(ln)]
        #tuple
        elif etp is VALUE_TYPES.TUPLE:
            ln = self.get_value(ensure_type=VALUE_TYPES.INT)
            return tuple((self.get_value() for i in range(ln)))
        #set
        elif etp is VALUE_TYPES.SET:
            ln = self.get_value(ensure_type=VALUE_TYPES.INT)
            return set((self.get_value() for i in range(ln)))
        #None
        elif etp is VALUE_TYPES.NONE:
            return None
        elif etp is VALUE_TYPES.CUSTOM:
            obj_id = self.get_value(ensure_type=VALUE_TYPES.INT)
            _ = self.get_value(ensure_type=VALUE_TYPES.INT)
            obj_type = self.conv_lookup.id_to_obj[obj_id]
            return obj_type.__reconstruct__(self)
        else:
            raise ValueError("Wrong type byte")
                    
    def has_values(self):
        return self.io.has_values()


def decode(data):
    dec = Decoder(data)
    while dec.has_values():
        yield dec.get_value()






        
    
    
