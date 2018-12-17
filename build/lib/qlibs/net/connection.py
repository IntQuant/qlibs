from collections import deque

BYTE_ORDER = 'big'
INT_SIZE = 4

def num_to_b(inp, size=INT_SIZE):
    return inp.to_bytes(size, BYTE_ORDER)

def b_to_num(inp):
    return int.from_bytes(inp, BYTE_ORDER)

class AsyncAdvWriter():
    def __init__(self, writer):
        self.writer = writer
    def write(self, data):
        self.writer.write(num_to_b(len(data)))
        self.writer.write(data)
    def write_num(self, data):
        self.write(num_to_b(data))
    
    async def drain(self):
        await self.writer.drain()
    def close(self):
        self.writer.close()
        
    
class AsyncAdvReader():
    def __init__(self, reader):
        self.reader = reader
    async def read(self):
        size = b_to_num(await self.reader.read(INT_SIZE))
        return await self.reader.read(size)
    async def read_num(self):
        return await b_to_num(self.read())

def AsyncAdvRW(AsyncAdvReader, AsyncAdvWriter):
    def __init__(self, socket):
        self.reader = socket
        self.writer = socket

class AdvRW():
    def __init__(self, socket):
        self.socket = socket
        self.current = b""
        self.packets = deque()
    def write(self, data):
        self.packets.append(num_to_b(len(data))+data)
        return self.send()
    
    def write_num(self, data):
        self.write(num_to_b(data))
        
    def send(self):
        if len(self.current) == 0:
            if len(self.packets) > 0:
                self.current = self.packets.popleft()
            else:
                return None
                    
        sent = self.socket.send(self.current)
        self.current = self.current[sent:]
        return sent
        
            
    def send_rep(self, attemps=10):
        while True:
            res = self.send()
            if res is None:
                return
            if res == 0:
                attemps -= 1
                if attemps <= 0:
                    return
    
    def read(self):
        size = b_to_num(self.socket.recv(INT_SIZE))
        return self.socket.recv(size)    
    
    def read_num(self):
        return b_to_num(self.read())
    
    def close(self):
        self.socket.close()

