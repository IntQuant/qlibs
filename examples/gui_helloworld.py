from qlibs.gui.widgets.behaviors import *
from qlibs.gui.widgets.app import App

def cb(name):
    exit(0)

mainnode = ColumnPlacerB()
mainnode.add_child(ButtonB("helloworld", print, "Hello, world!"))
mainnode.add_child(ButtonB("exit", cb))

app = App(mainnode)
while not app.should_close:
    app.render()