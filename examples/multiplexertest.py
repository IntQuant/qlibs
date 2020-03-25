"""
  Requires multiplexer server to be lauched first (see multiplexer_server.py example)
"""

from qlibs.net.multiplexer import MultiplexClient, MultiplexServer
from qlibs.gui.widgets.app import App
from qlibs.gui.widgets.behaviors import *
from time import sleep
import random


#port = random.randint(2000, 20000)

#MultiplexServer(host="127.0.0.1", port=port).serve_in_thread()

class Engine:
    def __init__(self):
        self.counter = 0
    
    def step(self, dt, events):
        for event in events:
            print(event)
            if event.name == "payload":
                if event.data == b"add":
                    self.counter += 1
                elif event.data == b"sub":
                    self.counter -= 1
        
    @property
    def state(self):
        pass
    
    @state.setter
    def _(self, to):
        pass
        
engine = Engine()
client = MultiplexClient(engine)
client.thread_runner()
client.min_step_time = 0.1
#client.send_payload(b"test_data")

def add_one(x):
    client.send_payload(b"add")

def sub_one(x):
    client.send_payload(b"sub")

label = NodeB()
button_add = ButtonB("+", add_one)
button_sub = ButtonB("-", sub_one)

buttons = RowPlacerB()
buttons.add_child(button_add)
buttons.add_child(button_sub)
node = ColumnPlacerB()
node.add_child(label)
node.add_child(buttons)
app = App(node)

while not app.should_close:
    label.text = str(engine.counter)
    app.render(0.1)

client.stop_thread()