import math
from numbers import Number
from array import array

import warnings
#from ..net.qpacket import conv_lookup, convert, make_qlibs_obj_id

VERTNAMES = {"x": 0, "y": 1, "z": 2, "w": 3}
NUMERICAL = Number

class VecBase:
    __slots__ = tuple()
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

    def __str__(self):
        return ", ".join(map(str, self))

    def __repr__(self):
        return "Vec(" + ", ".join(map(str, self)) + ")"

    def map_by_verticle(self, other, function: callable):
        assert len(self) == len(other), "wrong dimensions"
        return self.__class__(*[function(x, y) for x, y in zip(self, other)])

    def dot(self, other):
        return sum((v1 * v2 for v1, v2 in zip(self, other)))

    def cross(self, other): #Probably need to move this to Vec3
        x = self.y * other.z - self.z * other.y
        y = self.z * other.x - self.x * other.z
        z = self.x * other.y - self.y * other.x
        vec = self.__class__(x, y, z)
        return vec

    def __add__(self, other):
        #return self.map_by_verticle(other, lambda x, y: x + y)
        return self.__class__(*[v1+v2 for v1, v2 in zip(self, other)])

    def __iadd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        return self.map_by_verticle(other, lambda x, y: x - y)

    def __isub__(self, other):
        return self.__sub__(other)

    def __mul__(self, other):
        if isinstance(other, Vec):
            return self.map_by_verticle(other, lambda x, y: x * y)
        elif isinstance(other, NUMERICAL):
            return self.__class__(*map(lambda x: x * other, self))
        else:
            return NotImplemented

    def __imul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Vec):
            return self.map_by_verticle(other, lambda x, y: x / y)
        elif isinstance(other, NUMERICAL):
            return self.__class__(*map(lambda x: x / other, self))
        else:
            raise TypeError("Cannot divide vector by " + str(type(other)))

    def __itruediv__(self, other):
        return self.__truediv__(other)

    def __floordiv__(self, other):
        if isinstance(other, Vec):
            return self.map_by_verticle(other, lambda x, y: x / y)
        elif isinstance(other, NUMERICAL):
            return self.__class__(*map(lambda x: x // other, self))
        else:
            raise TypeError("Cannot divide vector by " + str(type(other)))

    def __ifloordiv__(self, other):
        return self.__floordiv__(other)

    def __pos__(self):
        return self

    def __neg__(self):
        return self.__class__(*map(lambda x: -x, self))

    def __abs__(self):
        return self.__class__(*map(abs, self))

    def normalized(self):
        ln = self.len()
        return self.__class__(*map(lambda x: x / ln, self))

    def len_sqr(self):
        return math.fsum(map(lambda x: x ** 2, self))

    def len(self):
        return math.sqrt(self.len_sqr())

    def to_tuple(self):
        return tuple(self._v)

    def bytes(self, dtype="f"):
        return array("f", self).tobytes()

    def normalize(self):
        ln = self.len()
        for i, e in enumerate(self):
            self[i] = e / ln

    def as_n_d(self, n):
        if n <= len(self):
            return self.__class__(self._v[:n])
        else:
            return self.__class__(self._v + ([0] * (n - len(self))))


class Vec(VecBase):  # Making those immutable is a good idea, right? (No)
    __slots__ = ("_v",)

    def __init__(self, *args):
        if len(args) == 1:
            self._v = list(args[0])
        else:
            self._v = list(args)

        #for v in self.v:
        #    assert isinstance(v, Number)

    def normalize(self):
        ln = self.len()
        for i, e in enumerate(self):
            self._v[i] = e / ln

    def __len__(self):
        return len(self._v)

    def __iter__(self):
        return iter(self._v)

    def __reversed__(self):
        return reversed(self._v)

    def __getitem__(self, key):
        return self._v[key]

    def __setitem__(self, key, value):
        self._v[key] = value

    def __getattr__(self, name):
        if name in VERTNAMES:
            ind = VERTNAMES[name]
            return self._v[ind]

    def __setattr__(self, name, value):
        if name in VERTNAMES:
            ind = VERTNAMES[name]
            self[ind] = value
        else:
            super().__setattr__(name, value)

    def __getstate__(self): return self._v
    def __setstate__(self, d): self._v = d


class Vec2(VecBase):
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __len__(self):
        return 2

    def __iter__(self):
        return iter((self.x, self.y))

    def __reversed__(self):
        return [self.y, self.x]

    def __getitem__(self, key):
        if key == 0:
            return self.x
        if key == 1:
            return self.y
        raise KeyError("Index can be one of 0, 1 for vec2 (%s passed)" % key)
        
    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
            return
        if key == 1:
            self.y = value
            return
        raise KeyError("Index can be one of 0, 1 for vec2 (%s passed)" % key)

    def __add__(self, oth):
        return Vec2(self.x+oth.x, self.y+oth.y)
    
    def __neg__(self):
        return self.__class__(-self.x, -self.y)

    @property
    def angle(self) -> float:
        return math.atan2(self.y, self.x)
    
    @angle.setter
    def _(self, value):
        l = self.len()
        self.x, self.y = math.cos(value)*l, math.sin(value)*l
    
    def rotate(self, angle) -> "Vec2":
        c = self.angle + angle
        l = self.len()
        return Vec2(math.cos(c)*l, math.sin(c)*l)


MVec = Vec
IVec = Vec
#conv_lookup.register(IVec, make_qlibs_obj_id(1))
#conv_lookup.register(MVec, make_qlibs_obj_id(2))
