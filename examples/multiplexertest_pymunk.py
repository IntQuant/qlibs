"""
  Requires multiplexer server to be lauched first (see multiplexer_server.py example)
  Note: requires pymunk to be install
  Note: uses pickle over network, which is not secure
"""

from qlibs.net.multiplexer import MultiplexClient, MultiplexServer
from qlibs.gui.window import Window
from qlibs.gui.basic_shapes import ShapeDrawer
from qlibs.math import Matrix4
from qlibs.gui.widgets.behaviors import *
from time import sleep
import random
import pickle #TODO: Not quite safe

import moderngl
import pymunk

#port = random.randint(2000, 20000)
#MultiplexServer(host="127.0.0.1", port=port).serve_in_thread()


class Engine:
    def __init__(self):
        self.space = pymunk.Space()
        b = pymunk.Body(body_type=pymunk.Body.STATIC)
        s = pymunk.Poly.create_box(b, (800, 50))
        s.friction=0.7
        self.space.add(b, s)
        
        self.space.gravity = (0.0, -90.0)
        self.things = []
    
    def step(self, dt, events):
        for event in events:
            print(event)
            if event.name == "payload":
                d = pickle.loads(event.data)
                if d[0] == "add":
                    b = pymunk.Body()
                    b.position = d[1]
                    s = pymunk.Poly.create_box(b)
                    s.density = 1
                    s.friction=0.7
                    self.space.add(b, s)
                    #self.things.append(s)
                    #self.things.append(b)
                    print("Added body")
        for i in range(5):
            self.space.step(0.1/5)
        
    @property
    def state(self):
        pass
    
    @state.setter
    def _(self, to):
        pass
        
engine = Engine()
client = MultiplexClient(engine)
client.min_step_time=0.01
client.thread_runner()

win = Window()

def on_mouse_click(window, button, action, mods):
    if action:
        d = ("add", win.mouse_pos)
        p = pickle.dumps(d)
        print(d, p)
        client.send_payload(p)

win.mouse_button_callback = on_mouse_click
win.flip_mouse_y = False

drawer = ShapeDrawer(win.ctx)

while not win.should_close:
    win.ctx.clear()
    win.ctx.enable_only(moderngl.BLEND)
    mvp = Matrix4.orthogonal_projection(0, win.width, 0, win.height, -1, 1)
    #print(len(engine.space.shapes))
    #print(end="\r")
    for shape in engine.space.shapes:
        #print(shape.body.position, end=" ")
        drawer.add_polygon([v.rotated(shape.body.angle) + shape.body.position for v in shape.get_vertices()])
    

    drawer.render(mvp=mvp)
    win.swap()
    win.wait_events(0.01)


client.stop_thread()