from ...math import IVec

class GUIEvent:
    def __init__(self):
        self.type = "gui"
        self.shall_pass = True


class MouseEvent(GUIEvent):
    def __init__(self, x, y, pressed):
        self.type = "mouse"
        self.shall_pass = True
        self.pos = IVec(x, y)
        self.pressed = pressed
