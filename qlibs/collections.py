from collections import deque

class ByteBuffer:
    def __init__(self, data=None, join_with=""):
        if data is not None:
            self.data = deque((data,))
        else:
            self.data = deque()
        self.join_with = join_with
    
    def read(self, read_size):
        try:
            len_found = 0
            collected = []
            while len_found < read_size:
                d = self.data.popleft()
                left = read_size - len_found
                len_found += len(d)
                if len(d) > left:
                    collected.append(d[:left])
                    self.data.appendleft(d[left:])
                else:
                    collected.append(d)
            
            return self.join_with.join(collected)
        except IndexError as e:
            raise ValueError("Not enought values in buffer") from e
    
    def write(self, data):
        self.data.append(data)
    
    def peek(self, size=None):
        tl = 0
        pointer = 0
        while tl < size and pointer < len(self.data):
            tl += len(self.data[pointer])
            pointer += 1
        res = self.join_with.join((self.data[i] for i in range(pointer)))
        return res[:size]
            
    
    def has_values(self):
        return len(self.data) > 0 and any(map(lambda x: len(x)>0, self.data))

