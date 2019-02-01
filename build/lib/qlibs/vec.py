import math
from numbers import Number as number
from array import array

try:
    from net.qpacket import conv_lookup, convert, make_qlibs_obj_id
except ImportError:
    from .net.qpacket import conv_lookup, convert, make_qlibs_obj_id

VERTNAMES = {'x':0, 'y':1, 'z':2, 'w':3}
NUMERICAL = (number, int)
RAISE_ON_TUPLE = True

class Vec:
    def __init__(self, *args):
        if len(args) == 1:
            self.v = list(args[0])
        else:
            self.v = list(args)
        
            
        for v in self.v:
            assert isinstance(v, number)

    def __eq__(self, other):
        try:
            if len(self) != len(other):
                return False
            
            for x, y in zip(self, other):
                if x != y:
                    return False
            return True
        except Exception:
            return False
    
    def __len__(self):
        return len(self.v)
    
    def __iter__(self):
        return iter(self.v)
    
    def __reversed__(self):
        return reversed(self.v)
    
    def __getitem__(self, key):
        return self.v[key]
    
    def __setitem__(self, key, value):
        self.v[key] = value

    def __getattr__(self, name):
        if name in VERTNAMES:
            ind = VERTNAMES[name]
            return self.v[ind]
        
    def __setattr__(self, name, value):
        if name in VERTNAMES:
            ind = VERTNAMES[name]
            self[ind] = value
        else:
            super().__setattr__(name, value)

    def __str__(self):
        return ", ".join(map(str, self.v))

    def __repr__(self):
        return "Vec(" + ", ".join(map(str, self.v)) + ")"
    
    def map_by_verticle(self, other, function:callable):
        assert len(self) == len(other), "wrong dimensions"
        return self.__class__([function(x, y) for x, y in zip(self, other)])
    
    def intify(self):
        self.v = list(map(int, self.v))
    
    def dot(self, other):
        return sum((v1 * v2 for v1, v2 in zip(self, other)))
                    
    def cross(self, other):
        vec = Vec(0, 0, 0) #TODO: change to indexes
        vec.x = self.y * other.z - self.z * other.y
        vec.y = self.z * other.x - self.x * other.z
        vec.z = self.x * other.y - self.y * other.x
        return vec
        
    def __add__(self, other):
        return self.map_by_verticle(other, lambda x,y:x+y)
    
    def __iadd__(self, other):
        return self.__add__(other)
    
    def __sub__(self, other):
        return self.map_by_verticle(other, lambda x,y:x-y)
    
    def __isub__(self, other):
        return self.__sub__(other)
    
    def __mul__(self, other):
        if isinstance(other, Vec):
            return self.map_by_verticle(other, lambda x,y:x*y)
        elif isinstance(other, NUMERICAL):
            return self.__class__(map(lambda x:x*other, self.v))
        else:
            return NotImplemented
    
    def __imul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):        
        if isinstance(other, Vec):
            return self.map_by_verticle(other, lambda x,y:x/y)
        elif isinstance(other, NUMERICAL):
            return self.__class__(map(lambda x:x/other, self.v))
        else:
            raise TypeError("Cannot divide vector by " + str(type(other)))
    
    def __itruediv__(self, other):        
        return self.__truediv__(other)
    
    def __floordiv__(self, other):        
        if isinstance(other, Vec):
            return self.map_by_verticle(other, lambda x,y:x/y)
        elif isinstance(other, NUMERICAL):
            return self.__class__(map(lambda x:x//other, self.v))
        else:
            raise TypeError("Cannot divide vector by " + str(type(other)))

    
    def __ifloordiv__(self, other):        
        return self.__floordiv__(other)
    

    def len_sqr(self):
        return math.fsum(map(lambda x:x**2, self.v))


    def len(self):
        return math.sqrt(self.len_sqr())
    
    def normalize(self):
        ln = self.len()
        for i, e in enumerate(self.v): 
            self.v[i] = e / ln
    
    def __pos__(self):
        return self
    
    
    def __neg__(self):
        return self.__class__(map(lambda x:-x, self.v))
    
    
    def __abs__(self):
        return self.__class__(map(abs, self.v))
    
    
    def to_tuple(self):
        return tuple(self.v)
        
    def __convert__(self):
        return convert(self.v)
    
    @classmethod
    def __reconstruct__(cls, decoder):
        obj = cls(list(decoder.get_value()))
        return obj

    def as_n_d(self, n):
        if n <= len(self):
            return self.__class__(self.v[:n])
        else:
            return self.__class__(self.v + ([0] * (n - len(self))))
    
    def bytes(self, dtype='f'):
        return array('f', self.v).tobytes()
            

conv_lookup.register(Vec, make_qlibs_obj_id(1))

if __name__ == "__main__":
    v1 = Vec(1, 2)
    v2 = Vec(1, 2)
    v3 = Vec(1, 3)
    
    assert v1.x == 1
    
    
    assert str(v3) == "1, 3"
    print(repr(v3))
    assert repr(v3) == "Vec(1, 3)"
    print(0, v1 + v2)
    print(1, v1 * v2)
    print(2, v3 * 10)
    print(3, -v3)
    try:
        v1 * "error"
    except Exception as e:
        assert "multiply" in str(e)
    else:
        raise AssertionError("No error while multiplying")
    
    print(v1 / 10)
    try:
        v1 / "error"
    except Exception as e:
        assert "Cannot divide" in str(e)
    else:
        raise AssertionError("No error while division")
    
    
    
    
    
