from net.qpacket import *
from qvec import Vec

if __name__ == "__main__":
    
    data = [1, 2, (-3, 4, (1, 3, -5.1, 1.5, None)), [b"test", "test"], Vec(1, 2)]
    
    conv = convert(data)
    
    d = Decoder(conv)
    
    print(conv)
    
    while d.has_values():
        v = d.get_value()
        print(v)
        print(v == data)
