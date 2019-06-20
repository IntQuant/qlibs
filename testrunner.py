import unittest

from qlibs.net.qpacket import *
from qlibs.math.vec import IVec, MVec
from qlibs.math.matrix import Matrix4, IDENTITY
from qlibs.net import connection as cn
from socket import socketpair

class QPacketTestCase():#unittest.TestCase):
    def test_int(self):
        for data in range(-100, 100):
            self.assertTrue(data == list(decode(convert(data)))[0])

    def test_float(self):
        for udata in range(-100, 100):
            data = float(udata)
            self.assertTrue(data == list(decode(convert(data)))[0])

    def test_bytes(self):
        data = b"testaafdsfasdf"
        self.assertTrue(data == list(decode(convert(data)))[0])

    def test_str(self):
        data = "testaafdsfasdf"
        self.assertTrue(data == list(decode(convert(data)))[0])

    def test_mult(self):
        data = [1, 2, b"12", "341"]
        r = []
        s = b"".join(map(convert, data))

        d = Decoder(s)

        while d.has_values():
            r.append(d.get_value())

        self.assertTrue(data == r)

    def test_compl(self):
        data = [1, 2, (-3, 4, (1, 3, -5.1, 1.5, None)), [b"test", "test"], MVec(1, 2)]
        self.assertTrue(data == list(decode(convert(data)))[0])


class VecTestCase(unittest.TestCase):
    def test_dot(self):
        self.assertTrue(MVec(-12, 16).dot(MVec(12, 9)) == 0)

    def test_cross(self):
        self.assertTrue(MVec(2, 3, 4).cross(MVec(5, 6, 7)) == MVec(-3, 6, -3))

    def test_equality(self):
        self.assertTrue(MVec(1, 2) == MVec(1, 2))
        self.assertTrue(MVec(1, 3) == MVec(1, 3))

    def test_inequality(self):
        self.assertTrue(MVec(1, 3) != MVec(1, 2))
        self.assertTrue(MVec(1, 30) != 1)

    def test_as_n_d(self):
        self.assertTrue(len(MVec(1, 3).as_n_d(4)) == 4)
        self.assertTrue(len(MVec(1, 3).as_n_d(1)) == 1)

    def test_normalize(self):
        v = MVec(1, 2, 3)
        v.normalize()
        self.assertTrue(v.len() == 1)


class MatrixTestCase(unittest.TestCase):
    def test_multiply_identity(self):
        mat1 = Matrix4(IDENTITY)
        mat2 = Matrix4(IDENTITY)
        mat3 = Matrix4(IDENTITY)
        self.assertTrue(mat1 * mat2 == mat3)

    def test_multiply_vector(self):
        mat = Matrix4(IDENTITY)
        vec = MVec(1, 2, 3, 1)
        self.assertTrue(mat * vec == vec)

    def test_look_at(self):
        res = Matrix4(
            [
                0.0,
                0.0,
                1.0,
                0.0,
                1.0,
                0.0,
                -0.0,
                0.0,
                -0.0,
                1.0,
                -0.0,
                0.0,
                -0.0,
                -0.0,
                -10.0,
                1.0,
            ]
        )
        self.assertTrue(
            Matrix4.look_at(IVec(10, 0, 0), IVec(0, 0, 0), IVec(0, 0, 1)) == res
        )

if __name__ == "__main__":
    unittest.main()
