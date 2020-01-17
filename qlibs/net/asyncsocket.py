"""
  Async socket library
"""
from collections import deque
from socket import SocketType
import selectors
from enum import Enum

from ..collections import ByteBuffer
from typing import Union, Tuple, Any, Callable

import logging

__all__ = ["AsyncSocket", "AsyncUDPSocket", "PacketSocket", "ServerSelector", "SelSockType", "bytes_packet_sender", "bytes_packet_reciever"]

logger = logging.getLogger("qlibs.net.asyncsocket")

RECVSIZE = 1024 * 8

class AsyncSocket:
    """
      Async socket - writing and reading don't block.
      
      Most useful when it is the only socket you need, consider using select if you
      need more sockets

      TCP version
    """
    extra = None
    def __init__(self, socket: SocketType):
        """Initialize using socket"""
        self.socket = socket
        self.socket.settimeout(0)
        self.buff = ByteBuffer(join_with=b"")
        self.send_size = 1024 * 8 #8kib
        self.closed = False
    
    def recv(self, amount: int) -> bytes:
        """Try to recieve data from socket"""
        try:
            res = self.socket.recv(amount)
            if len(res) == 0:
                logger.debug("Nothing recieved, assuming connection is closed")
                self.closed = True
            return res
        except BlockingIOError:
            return b""
    
    def send(self, data: bytes = None) -> int:
        """Try to send data to socket; this is buffered"""
        if data is not None:
            self.buff.write(data)
        data_to_send = self.buff.peek(self.send_size)
        try:
            res = self.socket.send(data_to_send)
        except BlockingIOError:
            return 0
        else:
            self.buff.read(res)
            return res
    
    def accept(self) -> Union[Tuple[SocketType, Any], Tuple[None, None]]:
        """Accept connection asynchronously. Returns (None, None) is not ready"""
        try:
            return self.socket.accept()
        except BlockingIOError:
            return None, None
    
    def empty(self) -> bool:
        """True if no values to send left"""
        return not self.buff.has_values()

    def fileno(self):
        return self.socket.fileno()
    
    def close(self):
        self.socket.close()

class PacketSocket:
    """
      Socket for handling packets, passes recieved bytes to generator
    """
    extra = None
    def __init__(self, socket, processor, *args):
        """**processor** should be a generator. 
        It will recieve new byte when recieving message.
        Use `data = yield` to recieve one byte as int value
        """
        
        self.socket = AsyncSocket(socket)
        self._gen = processor(self, *args)
        

        self._gen.send(None)
        self.reset = False
        self.storage = []
    
    def send(self, data:bytes = None):
        """Try to send data to socket; this is buffered"""
        try:
            self.socket.send(data)
        except (ConnectionResetError, OSError) as e:
            logger.debug(e)
            self.reset = True
    
    def recv(self, size=RECVSIZE):
        """Recieve data from socket and feed it to generator"""
        result = self.storage
        result.clear()
        try:
            data = self.socket.recv(size)
            for b in data:
                res = self._gen.send(b)
                if res is not None:
                    result.append(res)
            return result
        except (ConnectionResetError, OSError) as e:
            if self.closed:
                logger.debug("Attemped recieving from a closed socket")
            self.reset = True
            #print(e) #Probably need to remove this, hovewer useful when sockets are broken
            return result
    
    @property
    def closed(self):
        return self.reset or self.socket.closed

    def empty(self):
        """True if no values to send left"""
        return self.socket.empty()

    def fileno(self):
        return self.socket.fileno()
    
    def close(self):
        self.socket.close()

class AsyncUDPSocket:
    """
      Async socket - writing and reading don't block
      
      Most useful when it is the only socket you need, consider using select if you
      need more sockets

      UDP version
    """
    extra = None
    def __init__(self, socket):
        self.socket = socket
        self.socket.settimeout(0)
        self.buff = deque()
    
    def recv(self, amount=RECVSIZE):
        """Recieve data, (None, None) returned if no data available"""
        try:
            return self.socket.recvfrom(amount) #data, adress
        except BlockingIOError:
            return None, None
    
    def sendto_buff(self, data, adress):
        """Try to send packet to adress; with buffer"""
        self.buff.append((data, adress))
        counter = 0
        while self.buff:
            try:
                res = self.socket.sendto(*self.data[0]) #TODO: add hostname resolution
                counter += 1
                self.data.popleft()
            except BlockingIOError:
                break
            
        return counter
        
    def sendto(self, data, adress):
        """Try to send packet to adrees; no buffer"""
        try:
            res = self.socket.sendto(data, adress) #TODO: add hostname resolution
            return True
        except BlockingIOError:
            return False
    
    
class SelSockType(Enum):
    ACCEPTER = "accept"
    NORMAL = "normal"


class ServerSelector:
    def __init__(self, listener: SocketType, on_connect: Callable, on_read: Callable):
        self.selector = selectors.DefaultSelector()
        self.on_connect = on_connect
        self.on_read = on_read
        self.sock = AsyncSocket(listener)
        self.sockets = dict()
        self.selector.register(self.sock.socket, selectors.EVENT_READ, SelSockType.ACCEPTER)
    
    def select(self, timeout=None):
        events = self.selector.select(timeout)
        for key, mask in events:
            if mask & selectors.EVENT_READ:
                if key.data is SelSockType.ACCEPTER:
                    self._on_connect()
                if key.data is SelSockType.NORMAL:
                    self.on_read(self.sockets[key.fd])
            if mask & selectors.EVENT_WRITE:
                try:
                    self.sockets[key.fd].send()
                except KeyError as e:
                    pass #Socket is already unregistered, but selector still selected it

    def register(self, asock: Union[AsyncSocket, PacketSocket]):
        key = asock.socket.fileno()
        self.sockets[key] = asock
        self.selector.register(asock.socket, selectors.EVENT_READ | selectors.EVENT_WRITE, SelSockType.NORMAL)

    def unregister(self, asock: Union[AsyncSocket, PacketSocket]):
        key = asock.socket.fileno()
        self.selector.unregister(asock.socket)
        del self.sockets[key]
    
    @property
    def socket_iterator(self):
        return self.sockets.values()

    def _on_connect(self):
        sock, addr = self.sock.accept()
        if sock is None:
            return
        reg = self.on_connect(sock, addr)
        if reg is not None:
            self.register(reg)
        
    
def bytes_packet_sender(data):
    n = len(data)
    lres = list()
    while n > 0b1111111:
        lres.append((n & 0b1111111) | 0b10000000)
        n >>= 7
    lres.append(n)
    return bytes(lres) + data

def bytes_packet_reciever(sock):
    while True:
        l = 0
        n = 0b10000000
        i = 0
        while n & 0b10000000 > 0:
            n = yield
            l = l + ((n & 0b1111111) << (7*i))
            i += 1
        res = []
        for _ in range(l):
            res.append((yield))
        sock.storage.append(bytes(res))
            
                
            


    