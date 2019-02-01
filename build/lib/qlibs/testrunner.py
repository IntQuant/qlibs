import unittest

from net.qpacket import *
from vec import Vec
from matrix import Matrix4, IDENTITY
import net.connection as cn
from socket import socketpair

class QPacketTestCase(unittest.TestCase):
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
        data = [1, 2, (-3, 4, (1, 3, -5.1, 1.5, None)), [b"test", "test"], Vec(1, 2)]
        self.assertTrue(data == list(decode(convert(data)))[0])

class VecTestCase(unittest.TestCase):
    def test_dot(self):
        self.assertTrue(Vec(-12, 16).dot(Vec(12, 9)) == 0)
    
    def test_cross(self):
        self.assertTrue(Vec(2, 3, 4).cross(Vec(5, 6, 7)) == Vec(-3, 6, -3))
    
    def test_equality(self):
        self.assertTrue(Vec(1, 2) == Vec(1, 2))
        self.assertTrue(Vec(1, 3) == Vec(1, 3))
    
    def test_inequality(self):
        self.assertTrue(Vec(1, 3) != Vec(1, 2))
        self.assertTrue(Vec(1, 30) != 1)
    
    def test_as_n_d(self):
        self.assertTrue(len(Vec(1, 3).as_n_d(4)) == 4)
        self.assertTrue(len(Vec(1, 3).as_n_d(1)) == 1)
    
    def test_normalize(self):
        v = Vec(1, 2, 3)
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
        vec = Vec(1, 2, 3, 1)
        self.assertTrue(mat * vec == vec)
    
    def test_look_at(self):
        res = Matrix4([0.0, 0.0, 1.0, 0.0, 1.0, 0.0, -0.0, 0.0, -0.0, 1.0, -0.0, 0.0, -0.0, -0.0, -10.0, 1.0])
        self.assertTrue(Matrix4.look_at(Vec(10, 0, 0), Vec(0, 0, 0), Vec(0, 0, 1)) == res)

'''
class ConnectonTestCase(unittest.TestCase):
    def test_send_recieve(self):
        

        sock0, sock1 = socketpair()

        
        cn0 = cn.RWConvertable(sock0)
        
        cn1 = cn.RWConvertable(sock1)

        
        sent = [1, 2, 3]
        cn0.write(sent)
        cn0.write(sent)
        cn0.write("test")
        
        cn0.send_rep()
        
        
        cn1.recv_data()
        
        self.assertTrue(cn1.read() == sent)
        self.assertTrue(cn1.read() == sent)
        self.assertTrue(cn1.read() == None)
'''
        
if __name__ == "__main__":
    unittest.main()
