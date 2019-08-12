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


class KeyMods:
    def __init__(self, glfwmods=0):
        self.shift = glfwmods&1 > 0
        self.ctrl = glfwmods&2 > 0
        self.alt = glfwmods&4 > 0
        self.super = glfwmods&8 > 0
        self.caps = glfwmods&16 > 0
        self.numlock = glfwmods&32 > 0


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
