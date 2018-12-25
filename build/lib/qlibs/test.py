import net.connection as cn
from socket import socketpair

sock0, sock1 = socketpair()

print("cn0 created")
cn0 = cn.RWConvertable(sock0)
print("cn1 created")
cn1 = cn.RWConvertable(sock1)

print("Writing to cn0")
cn0.write([1, 2, 3])
cn0.write([1, 2, 3])
cn0.write("test")
print("Serving cn0")
cn0.send_rep()
#print(cn0.serve())
print("Serving cn1")
cn1.recv_data()
print(cn1.debug_data())
print(cn1.read())
print(cn1.read())
print(cn1.read())
