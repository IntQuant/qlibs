import unittest

from net.qpacket import *
from vec import Vec

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
        
if __name__ == "__main__":
    unittest.main()

if __name__ == "__main__ d":
    
    
    
    conv = convert(data)
    
    d = Decoder(conv)
    
    print(conv)
    
    while d.has_values():
        v = d.get_value()
        print(v)
        print(v == data)
