from collections import deque
from enum import Enum
from qlibs.gui.widgets.behaviors import *
from typing import Any, Callable, Tuple, Union
import warnings

import moderngl

from qlibs.fonts.font_render import DirectFontRender, FormattedText
from qlibs.math import Matrix4, Vec2
from qlibs.gui.window import current_window, current_context
from qlibs.gui.basic_shapes import ShapeDrawer
from qlibs.gui.widgets.controller import is_selected_cb

from dataclasses import dataclass

V1_PARAMS_V0 = {
    "text_limit": 256,
    "max_text_size": 25,
    "fg_color": (0.2, 0.4, 0.5, 0.8),
    "fg_color_hov": (0.2, 0.4, 0.5, 0.8),
    "fg_color_sel": (0.1, 0.1, 1, 1),
    #"fg_color": (0.1, 0.1, 1, 1),
    #"fg_color_sel": (0.9, 0.9, 0, 1),
    "bg_color": (0.2, 0.2, 0.2, 0.8),
    "bg_color_sel": (0.05, 0.05, 0.05, 0.8),
}

class QueuedType(Enum):
    TEXT = "text"
    BG = "background"
    FGOUTLINE = "foreground_outline"
    FGLINE = "foreground_line"
    CUSTOM = "custom"


@dataclass
class QueuedText:
    type = QueuedType.TEXT
    text: str
    pos: Vec2
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    scale: float = 1
    scissor: Union[None, Tuple[Vec2, Vec2]] = None
    multiline: Union[None, int] = None


@dataclass
class QueuedBG:
    type = QueuedType.BG
    pos: Vec2
    size: Vec2
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)


@dataclass
class QueuedFGOutline:
    type = QueuedType.FGOUTLINE
    pos: Vec2
    size: Vec2
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    width: float = 2


@dataclass
class QueuedFGLine:
    type = QueuedType.FGLINE
    p0: Vec2
    p1: Vec2
    color: Tuple[float, float, float] = (1.0, 1.0, 1.0)
    width: float = 1


@dataclass
class QueuedCustom:
    type = QueuedType.CUSTOM
    func: Callable
    viewport: tuple
    args: tuple = tuple()


class V1Generator:
    def __init__(self, window=None, font_renderer=None):
        window = window or current_window.get()
        self.ctx = window.ctx
        self.font_render = font_renderer or DirectFontRender()
        self.font_render.flip_y = True
        self.window = window
        self.params = V1_PARAMS_V0.copy()        
        self.image_ident = 0
        self.render_queue = list()
        self.text_queue = list()
    
    @property
    def param_bg_color(self):
        return self.params["bg_color"]
    
    @property
    def param_bg_color_sel(self):
        return self.params["bg_color_sel"]
    
    @property
    def param_fg_color(self):
        return self.params["fg_color"]
    
    @property
    def param_fg_color_sel(self):
        return self.params["fg_color_sel"]

    def __getattr__(self, key):
        if key.startswith("param_"): #TODO - node-specific params
            return self.params[key[6:]]
        raise AttributeError("Unknown key %s" % key)

    def render_node(self, node: NodeB):
        self.image_ident = 0
        if node.type == "window":
            self.render_queue.extend(self.text_queue)
            self.text_queue.clear()

        if node.hidden:
            return
        highlighted = False
        selected = is_selected_cb.get()(node)
        if node.type in ["button", "togglebutton", "radiobutton"]:
            highlighted = node.hovered
            selected = node.pressed

        bg_color = None
        spc = 2
        if node.type in ["button", "textinput", "scrollbar", "togglebutton", "radiobutton", "progressbar", QlibsNodeTypes.COLUMN_DIAGRAM]:
            bg_color = self.param_bg_color_sel
        if node.type == "window":
            bg_color = self.param_bg_color
            spc = 0

        if bg_color is not None:
            self.render_queue.append(QueuedBG(pos=node.position+Vec2(spc, spc), size=node.size-Vec2(spc*2, spc*2), color=bg_color))

        if node.type == "window":
            self.render_queue.append(QueuedFGOutline(pos=node.position, size=node.size, color=self.param_fg_color))
            self.render_queue.append(QueuedBG(pos=node.position, size=node.header_size, color=self.param_fg_color))
        
        if selected or highlighted:
            color = (0, 0, 0, 0)
            if highlighted:
                color = self.param_fg_color_hov
            if selected:
                color = self.param_fg_color_sel
            self.render_queue.append(QueuedFGOutline(pos=node.position+Vec2(spc, spc), size=node.size-Vec2(spc*2, spc*2), color=color))
        
        if node.type == "progressbar":
            size = node.size-Vec2(8, 8)
            size.x *= node.fraction
            self.render_queue.append(QueuedBG(pos=node.position+Vec2(4, 4), size=size, color=self.param_fg_color))

        if node.type == "scrollbar":
            size = node.size-Vec2(8, 8)
            pos = node.position+Vec2(4, 4)
            pos.y += size.y * (node.pos*0.9)
            size.y *= 0.1
            self.render_queue.append(QueuedBG(pos=pos, size=size, color=self.param_fg_color))
        
        if node.type == "customrender":
            self.render_queue.extend(self.text_queue)
            self.text_queue.clear()
            viewport = (node.position.x, self.window.height-node.position.y-node.size.y, node.size.x, node.size.y)
            self.render_queue.append(QueuedCustom(node.render, args=(node,), viewport=viewport))

        if node.text is not None:
            if node.type == "text" or isinstance(node.text, FormattedText):
                pos = Vec2(*node.position)
                pos.y = self.window.height - pos.y - node.size.y
                scissor = (*pos, *node.size)
                self.text_queue.append(QueuedText(
                    text=node.text, 
                    pos=Vec2(node.position.x+4, node.position.y+node.scale), 
                    multiline=node.size.x-8, 
                    scissor=scissor,
                    scale=self.param_max_text_size,
                ))
            else:
                text = node.text
                used_scale = min(node.size.y, self.param_max_text_size)
                ident = 8
                size = self.font_render.calc_size(text, scale=used_scale)
                if size > 0 and size > node.size.x - self.image_ident - ident:
                    used_scale *= (node.size.x-self.image_ident-ident) / size
                    size = self.font_render.calc_size(text, scale=used_scale)

                align_ajust = node.size.x // 2 - size // 2
                pos = node.position + node.size // 2
                pos.x += self.image_ident + align_ajust - node.size.x // 2
                text_height = self.font_render.calc_height(text, scale=used_scale)
                if text_height == 0:
                    text_height = self.param_max_text_size
                pos.y += text_height // 2
                self.text_queue.append(QueuedText(text=text, pos=pos, scale=used_scale))
                if node.type == "textinput" and is_selected_cb.get()(node):
                    cpos = node.position.x + self.font_render.calc_size(text[:node.cursor], scale=used_scale) + align_ajust
                    cy = node.position.y+node.size.y/2
                    txh = min(text_height/2+5, (node.size.y)/2)
                    self.render_queue.append(QueuedFGLine(p0=Vec2(cpos, cy-txh), p1=Vec2(cpos, cy+txh), color=self.param_fg_color_sel, width=1))
            
            if node.type is QlibsNodeTypes.COLUMN_DIAGRAM:
                if node.displayed_data:
                    mx = max((x.value for x in node.displayed_data))
                    if mx == 0:
                        scale_y = 1
                    else:
                        scale_y = 1/mx
                    spx = 2
                    bspy = 30
                    diag_size_y = node.size.y - bspy
                    scale_y *= diag_size_y
                    size_x = min(node.size.x / len(node.displayed_data), 50)
                    for i, datum in enumerate(node.displayed_data):
                        datum_size = datum.value*scale_y
                        pos = Vec2(node.position.x+i*size_x, node.position.y+node.size.y-datum_size)
                        text = str(datum.value)
                        text_scale = 20
                        text_size = self.font_render.calc_size(text, scale=text_scale)
                        self.render_queue.append(QueuedBG(pos, Vec2(size_x-spx, datum_size), color=self.param_fg_color))
                        pos = Vec2(*pos)
                        if datum.tag is not None and datum_size < text_scale:
                            pos.y -= text_scale - datum_size
                        self.text_queue.append(QueuedText(text, pos+Vec2((size_x-text_size)/2, -4), scale=text_scale))
                        if datum.tag is not None:
                            text = datum.tag
                            text_size = self.font_render.calc_size(text, scale=text_scale)
                            pos = Vec2(node.position.x+i*size_x, node.position.y+node.size.y)
                            self.text_queue.append(QueuedText(text, pos+Vec2((size_x-text_size)/2, -4), scale=text_scale))

                
                
                

    def generate(self, node):
        self.render_queue.clear()
        queue = deque()
        queue.append(node)
        while queue:
            current = queue.pop()
            self.render_node(current)
            for child in current.children:
                queue.append(child)
        self.render_queue.extend(self.text_queue)
        self.text_queue.clear()
        return self.render_queue


class V1Renderer:
    def __init__(self, window=None, is_selected_cb=None):
        self.generator = V1Generator()
        self.ctx = current_context.get()
        self.win = current_window.get()
        self.drawer = ShapeDrawer()
        self.font = DirectFontRender()
        self.font.flip_y = True
    
    def render(self, node):
        queue = self.generator.generate(node)
        self.matrix = Matrix4.orthogonal_projection(0, self.win.width, self.win.height, 0, -1, 1)
        self.ctx.enable_only(moderngl.BLEND)
        last_state = None
        for el in queue:
            if el.type is QueuedType.BG:
                self.drawer.add_rectangle(*el.pos, *el.size, color=el.color)
            if el.type is QueuedType.TEXT:
                if last_state in [QueuedType.BG, QueuedType.FGOUTLINE]:
                    self.drawer.render(mvp=self.matrix)
                if el.multiline:
                    try:
                        self.ctx.scissor = el.scissor
                        self.font.render_multiline(el.text, el.pos.x, el.pos.y, el.multiline, mvp=self.matrix, scale=el.scale)
                    finally:
                        self.ctx.scissor = None
                else:
                    self.font.render_string(el.text, *el.pos, scale=el.scale, mvp=self.matrix)
            if el.type is QueuedType.FGOUTLINE:
                #self.drawer.add_line2d_rectangle(*el.pos, *el.size, color=el.color, width=el.width)
                self.drawer.add_line_rectangle(*el.pos, *el.size, color=el.color)
            if el.type is QueuedType.FGLINE:
                self.drawer.add_line2d(el.p0, el.p1, color=el.color, width=el.width)
            if el.type is QueuedType.CUSTOM:
                self.drawer.render(mvp=self.matrix)
                bak = self.ctx.viewport
                try:
                    self.ctx.viewport = el.viewport
                    #self.ctx.scissor = el.viewport
                    el.func(*el.args)
                    self.ctx.enable_only(moderngl.BLEND)
                finally:
                    self.ctx.viewport = bak
                    self.ctx.scissor = None
            last_state = el.type

        self.drawer.render(mvp=self.matrix)
