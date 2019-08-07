from ...math import IVec

class GUIEvent:
    type = "gui"
    shall_pass = True
    def __init__(self):
        self.shall_pass = True


class MouseEvent(GUIEvent):
    type = "mouse"
    def __init__(self, x, y, pressed):
        self.pos = IVec(x, y)
        self.pressed = pressed


class KeyEvent(GUIEvent):
    type = "key"
    def __init__(self, key, mods):
        self.key = key
        self.mods = mods

class SpecKeyEvent(GUIEvent):
    type = "speckey"
    def __init__(self, key, mods):
        self.key = key
        self.mods = mods
