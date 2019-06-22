import unittest

from qlibs.net.qpacket import *
from qlibs.math.vec import IVec, MVec
from qlibs.math.matrix import Matrix4, IDENTITY
from qlibs.net import connection as cn
from qlibs.resources import resource_loader
from socket import socketpair


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
                0.0, 0.0, 1.0, 0.0,
                1.0, 0.0, -0.0, 0.0,
                -0.0, 1.0, -0.0, 0.0,
                -0.0, -0.0, -10.0, 1.0,
            ]
        )
        self.assertTrue(
            Matrix4.look_at(IVec(10, 0, 0), IVec(0, 0, 0), IVec(0, 0, 1)) == res
        )


class LoaderTestCase(unittest.TestCase):
    def test_prefix_path(self):
        loader = resource_loader.Loader()
        res = loader.handle_prefix("a/b/c", "a/")
        self.assertEqual(res, "b/c")
        res = loader.handle_prefix("a/b/c", "a/b/")
        self.assertEqual(res, "c")
    
    def test_prefix_none(self):
        loader = resource_loader.Loader()
        res = loader.handle_prefix("a/b/c", "b/")
        self.assertEqual(res, None)

if __name__ == "__main__":
    unittest.main()
