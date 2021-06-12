import unittest

#from qlibs.net.qpacket import *
from qlibs.math.vec import IVec, MVec
from qlibs.math.matrix import Matrix4, IDENTITY, ZEROS_16
#from qlibs.net import connection as cn
from qlibs.resources import resource_loader
from socket import socketpair
from qlibs.collections import ByteBuffer

import qlibs.gui.basic_shapes
import qlibs.gui.sprite_drawer
import qlibs.gui.window
import qlibs.gui.widgets.behaviors
import qlibs.gui.widgets.controller
import qlibs.gui.widgets.render

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
        self.assertEqual(len(MVec(1, 3).as_n_d(4)), 4)
        self.assertEqual(len(MVec(1, 3).as_n_d(1)), 1)

    def test_normalize(self):
        v = MVec(1, 2, 3)
        v.normalize()
        self.assertTrue(v.len() == 1)


class MatrixTestCase(unittest.TestCase):
    def test_multiply_identity(self):
        mat1 = Matrix4(IDENTITY)
        mat2 = Matrix4(IDENTITY)
        mat3 = Matrix4(IDENTITY)
        self.assertEqual(mat1 * mat2, mat3)

    def test_multiply_vector(self):
        mat = Matrix4(IDENTITY)
        vec = MVec(1, 2, 3, 1)
        self.assertEqual(mat * vec, vec)

    def test_multiply_notimpl(self):
        mat = Matrix4(ZEROS_16)
        with self.assertRaises(TypeError):
            1 * mat
        with self.assertRaises(TypeError):
            mat * 1

    def test_look_at(self):
        res = Matrix4(
            [
                0.0, 0.0, 1.0, 0.0,
                1.0, 0.0, -0.0, 0.0,
                -0.0, 1.0, -0.0, 0.0,
                -0.0, -0.0, -10.0, 1.0,
            ]
        )
        self.assertEqual(
            Matrix4.look_at(IVec(10, 0, 0), IVec(0, 0, 0), IVec(0, 0, 1)), res
        )
    
    def test_bytes(self):
        mat = Matrix4(IDENTITY)
        b = mat.bytes()
        self.assertIsInstance(b, bytes)
        self.assertGreater(len(b), 15)

    def test_translation_matrix(self):
        m = Matrix4.translation_matrix(10, 5, 2)
        v = m*IVec(0, 0, 0, 1)
        self.assertEqual(v, IVec(10, 5, 2, 1))

    def test_scale_matrix(self):
        m = Matrix4.scale_matrix(3)
        v = m*IVec(1, 0, 0)
        self.assertEqual(v, IVec(3, 0, 0, 1))
    
    def test_str(self):
        mat = Matrix4(IDENTITY)
        v = mat.__str__()
        self.assertGreater(len(v), 20)
    
    def test_repr(self):
        mat = Matrix4(IDENTITY)
        v = repr(mat)
        self.assertGreater(len(v), 10)
        self.assertIn("Matrix4", v)
        mat = Matrix4([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
        v = repr(mat)
        self.assertGreater(len(v), 20)
        self.assertIn("Matrix4", v)
        mat = Matrix4(ZEROS_16)
        v = repr(mat)
        self.assertGreater(len(v), 10)
        self.assertIn("Matrix4", v)
    
    def test_inverse(self):
        mat = Matrix4([
            0.0, 0.0, 1.0, 0.0,
            1.0, 0.0, -0.0, 0.0,
            -0.0, 1.0, -0.0, 0.0,
            -0.0, -0.0, -10.0, 1.0,
        ])
        self.assertEqual(mat * mat.inverse(), Matrix4(IDENTITY))

        
    

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


class ByteBufferTestCase(unittest.TestCase):
    def test_init_none(self):
        bb = ByteBuffer()
        bb.write("a")
        bb.write("b")
        bb.write("cc")
        self.assertEqual("abc", bb.peek(3))
        self.assertEqual("abc", bb.read(3))
        self.assertTrue(bb.has_values())
        self.assertEqual("c", bb.read(1))
        self.assertFalse(bb.has_values())
    
    def test_init_string(self):
        bb = ByteBuffer("ttt")
        bb.write("a")
        bb.write("b")
        bb.write("cc")
        self.assertEqual("ttt", bb.read(3))
        self.assertEqual("abc", bb.peek(3))
        self.assertEqual("abc", bb.read(3))
        self.assertTrue(bb.has_values())
        self.assertEqual("c", bb.read(1))
        self.assertFalse(bb.has_values())
        

class FontLoaderTestCase(unittest.TestCase):
    #Test if it does not crash
    def test_win(self):
        import sys
        init_platform = sys.platform
        sys.platform = "win"
        try:
            qlibs.fonts.font_search.find_reasonable_font()
        finally:
            sys.platform = init_platform

    def test_linux(self):
        import sys
        init_platform = sys.platform
        sys.platform = "linux"
        try:
            qlibs.fonts.font_search.find_reasonable_font()
        finally:
            sys.platform = init_platform


if __name__ == "__main__":
    unittest.main()
