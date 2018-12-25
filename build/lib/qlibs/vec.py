import math
from numbers import Number as number

try:
    from .net.qpacket import conv_lookup, convert, make_qlibs_obj_id
except ImportError:
    from net.qpacket import conv_lookup, convert, make_qlibs_obj_id

VERTNAMES = {'x':0, 'y':1, 'z':2}
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
        if isinstance(self.v, tuple):
            self.v = list(self.v)
            print("Vectors V was tuple")
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
            if RAISE_ON_TUPLE and name == "v" and isinstance(value, tuple):
                raise ValueError("V set to tuple")
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
        
    def cross_product(self, other):
        return self.x * other.y - self.y * other.x;
    
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
            raise TypeError("Cannot multiply vector by " + str(type(other)))
    
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
        return sum(map(lambda x:x**2, self.v))


    def len(self):
        return math.sqrt(len_sqr(self))
    
    
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

conv_lookup.register(Vec, make_qlibs_obj_id(1))

if __name__ == "__main__":
    v1 = Vec([1, 2])
    v2 = Vec([1, 2])
    v3 = Vec([1, 3])
    
    assert v1 == v2
    assert not (v1 == 1)
    
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
        assert "Cannot multiply" in str(e)
    else:
        raise AssertionError("No error while multiplying")
    
    print(v1 / 10)
    try:
        v1 / "error"
    except Exception as e:
        assert "Cannot divide" in str(e)
    else:
        raise AssertionError("No error while division")
    
    
    
