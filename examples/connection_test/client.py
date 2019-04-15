import socket
import msvcrt

from qlibs.net.asyncsocket import AsyncSocket

sock = AsyncSocket(socket.create_connection(("localhost", 51235)))

while True:
    while msvcrt.kbhit():
        sock.send(msvcrt.getch())
    for c in sock.recv(1):
        msvcrt.putch(bytes([c]))
