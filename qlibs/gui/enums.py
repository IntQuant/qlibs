from enum import Enum, auto

class EventTypes(Enum):
    PRE_DRAW = auto()
    POST_DRAW = auto()

    MOUSE_MOTION = auto()
    MOUSE_RELEASE = auto()
    MOUSE_PRESS = auto()
    MOUSE_DRAG = auto()
    MOUSE_SCROLL = auto()

    TEXT = auto()
    TEXT_MOTION = auto()
    TEXT_MOTION_SELECT = auto()
