"""
  Example showing basically everything of widgets
"""

from logging import warning
import warnings

warnings.simplefilter("once", DeprecationWarning)

from qlibs.gui.widgets.behaviors import *
from qlibs.gui.widgets.app import App
from qlibs.highlevel.graphics import SpriteMaster


import time
import moderngl

centerer = WindowNodeB()
centerer.image_id = "eye"
centerer.image_mode = "fill"
centerer.image_ratio = 1 #y / x

placer = ColumnPlacerB()
#placer.spc = 20

bplacer1 = ScrollableListB()
for i in range(20):
    button = ButtonB(f"{i}", lambda x: print(f"hi from {x}"), text=f"Text on button {i}")
    bplacer1.add_child(button)

bplacer2 = ScrollableStringListB(callback=print)
for i in range(20):
    bplacer2.add_child(f"Text in stringlist {i}")
    
bplacers = RowPlacerB()
bplacers.add_child(bplacer1)
bplacers.add_child(bplacer2)
placer.add_child(bplacers)
placer.add_child(TextInputB(), 0.1)
placer.add_child(TextNodeB("lalalalalalal sdfad asdf asdfas dfasdf sadf asdfasd fsadf sadf asdf adsf asdf das asd"), 0.2)
row_placer = RowPlacerB()

row_placer.add_child(ToggleButtonB("togglable", lambda name, state: print(name, state)), 1)
b2 = ToggleButtonB("togglable", lambda name, state: print(name, state))
b2.image_id = "eye"
row_placer.add_child(b2, 1)
row_placer.add_child(TextInputB(callback=print))
    
row_placer.size_hint_func = hint_func_rel #Use hint function to make some widgets square


placer.add_child(row_placer, 0.1)

pb = ProgressBarB()

placer.add_child(pb, 0.1)

centerer.add_child(placer)

app = App(centerer, width=1000, height=800)

wnd2 = WindowNodeB()
wnd2.add_child(TextNodeB("lalalalalalal sdfad asdf asdfas dfasdf sadf asdfasd fsadf sadf asdf adsf asdf das asd"))
app.root_node.layers["wnd2"] = wnd2
wnd3 = WindowNodeB()
wnd3.add_child(TextNodeB("lalalalalalal sdfad asdf asdfas dfasdf sadf asdfasd fsadf sadf asdf adsf asdf das asd"))
app.root_node.layers["wnd3"] = wnd3

app.root_node.layers["main"].ext_docked = True

def docked_cb(name, v):
    app.root_node.layers["main"].ext_docked = v

row_placer.add_child(ToggleButtonB("docked", docked_cb, state=True), 1)

spritem = SpriteMaster(app.ctx)
spritem.load_file("eye", "qlibs/images/eye.png")
spritem.init()

app.rend.sprite_master = spritem
#app.rend.excludes.pop(0)
#app.rend.params["node_bg_color"] = (1, 1, 1, 0.5)

stime = time.time()
ttime = 10

while not app.should_close:
    app.render(wait_time=0.1)
    ptime = time.time() - stime
    pb.fraction = (ptime % ttime) / ttime
