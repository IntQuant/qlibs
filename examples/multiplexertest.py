from qlibs.net.multiplexer import MultiplexClient, MultiplexServer
from time import sleep
import random

port = random.randint(2000, 20000)

#MultiplexServer(host="127.0.0.1", port=port).serve_in_thread()
sleep(1)

class Engine:
    def __init__(self):
        self.s = b""
    
    def step(self, events):
        for event in events:
            print(event)
        
engine = Engine()
client = MultiplexClient(engine)
client.thread_runner()
client.send_payload(b"test_data")
