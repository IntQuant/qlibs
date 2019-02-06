import socket

sock = socket.socket()
sock.connect(("25.99.38.230", 42151))
print("Connected")
sock.send(b"HI")
print(sock.recv(1024))
