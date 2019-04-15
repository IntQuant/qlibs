import socket
import msvcrt

from qlibs.net.asyncsocket import AsyncSocket

ssock = socket.socket()
ssock.bind(("localhost", 51235))
ssock.listen()
rs, addr = ssock.accept()
sock = AsyncSocket(rs)

while True:
    while msvcrt.kbhit():
        sock.send(msvcrt.getch())
    for c in sock.recv(1):
        msvcrt.putch(bytes([c]))


