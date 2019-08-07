import socket
from enum import auto
from select import select

from qpacket import convert, BinaryAuto

#TODO

class ResponseType(BinaryAuto):
    DISCARDABLE = auto()
    ENSURED = auto()
    

class UDPLink():
    def __init__(self, addr, socket_type=socket.AF_INET, socket_mod=socket.SOCK_DGRAM):
        self.addr = addr
        self.socket_type = socket_type
        self.socket_mod = socket_mod
        self.socket = socket.socket()
        self.msg_id = 0
        self.pending_msgs = dict()
        self.to_send = deque()
        self.socket.setblocking(False)
    
    def serve(self):
        rsend, rrecv, rerr = select([self.socket], [self.socket], [self.socket])
        
        self.socket.sendto(self.to_send.popleft(), self.addr)
        #TODO: add recieving
        
    def send_raw_datagram(self, data:bytes):
        self.to_send.append(data)
    
    def send_datagram(self, data: "convertable"):
        self.send_raw_datagram(convert((ResponseType.DISCARDABLE.value, data)))
    
    def send_ensure(self, data: "convertable"):
        msg = convert((ResponseType.ENSURED, self.msg_id, data))
        self.pending_msgs[self.msg_id] = msg
        self.send_raw_datagram(msg)
        self.msg_id += 1
        
    
