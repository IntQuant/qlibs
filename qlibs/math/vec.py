import math
from numbers import Number
from array import array

from ..net.qpacket import conv_lookup, convert, make_qlibs_obj_id

VERTNAMES = {"x": 0, "y": 1, "z": 2, "w": 3}
NUMERICAL = Number


class IVec:  # Making those immutable is a good idea, right?
    """
      Immutable vector type
    """

    __slots__ = ("v",)

    def __init__(self, *args):
        if len(args) == 1:
            self.v = tuple(args[0])
        else:
            self.v = tuple(args)

        for v in self.v:
            assert isinstance(v, Number)

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
        raise AttributeError("Cannot modify immutable object")

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

    def map_by_verticle(self, other, function: callable):
        assert len(self) == len(other), "wrong dimensions"
        return self.__class__([function(x, y) for x, y in zip(self, other)])

    def dot(self, other):
        return sum((v1 * v2 for v1, v2 in zip(self, other)))

    def cross(self, other): #Probably need to move this to Vec3
        x = self.y * other.z - self.z * other.y
        y = self.z * other.x - self.x * other.z
        z = self.x * other.y - self.y * other.x
        vec = self.__class__(x, y, z)
        return vec

    def __add__(self, other):
        return self.map_by_verticle(other, lambda x, y: x + y)

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
            return self.__class__(map(lambda x: x * other, self.v))
        else:
            return NotImplemented

    def __imul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Vec):
            return self.map_by_verticle(other, lambda x, y: x / y)
        elif isinstance(other, NUMERICAL):
            return self.__class__(map(lambda x: x / other, self.v))
        else:
            raise TypeError("Cannot divide vector by " + str(type(other)))

    def __itruediv__(self, other):
        return self.__truediv__(other)

    def __floordiv__(self, other):
        if isinstance(other, Vec):
            return self.map_by_verticle(other, lambda x, y: x / y)
        elif isinstance(other, NUMERICAL):
            return self.__class__(map(lambda x: x // other, self.v))
        else:
            raise TypeError("Cannot divide vector by " + str(type(other)))

    def __ifloordiv__(self, other):
        return self.__floordiv__(other)

    def __pos__(self):
        return self

    def __neg__(self):
        return self.__class__(map(lambda x: -x, self.v))

    def __abs__(self):
        return self.__class__(map(abs, self.v))

    def normalized(self):
        ln = self.len()
        return self.__class__(map(lambda x: x / ln, self.v))

    def len_sqr(self):
        return math.fsum(map(lambda x: x ** 2, self.v))

    def len(self):
        return math.sqrt(self.len_sqr())

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

    def bytes(self, dtype="f"):
        return array("f", self.v).tobytes()


class MVec(IVec):
    """
      Mutable vector type
    """

    def __init__(self, *args):
        if len(args) == 1:
            self.v = list(args[0])
        else:
            self.v = list(args)

        for v in self.v:
            assert isinstance(v, Number)

    def __setitem__(self, key, value):
        self.v[key] = value

    def normalize(self):
        ln = self.len()
        for i, e in enumerate(self.v):
            self.v[i] = e / ln

Vec = MVec #Deprecated
conv_lookup.register(IVec, make_qlibs_obj_id(1))
conv_lookup.register(MVec, make_qlibs_obj_id(2))
