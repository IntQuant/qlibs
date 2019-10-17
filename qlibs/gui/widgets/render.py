from collections import deque

import moderngl

from ..basic_shapes import ShapeDrawer
from ...fonts.font_render import DirectFontRender
from ...fonts.font_search import find_reasonable_font
from ...math import Matrix4, MVec

DEFAULT_PARAMS = {
    "text_limit": 256,
    "max_text_size": 32,
    "pb_spacing_side": 4,
    "pb_spacing_main": 2,
    "node_bg_color": (1, 1, 1, 0.1),
    "node_border_color": (1, 1, 1, 0.2),
    "text_color": (1, 1, 1),
}

class DefaultRenderer:
    def __init__(self, window, node, font=None, font_path=None, font_render=None):
        if font is None and font_path is None:
            font_path = find_reasonable_font()
        self.ctx = window.ctx
        self.font_render = font_render or DirectFontRender(self.ctx, font, font_path=font_path)
        self.font_render.flip_y = True
        self.drawer = ShapeDrawer(self.ctx)
        self.node = node
        self.window = window
        self.text_queue = []
        self.excludes = ["centerer"]
        self.drawer.default_z = -1
        #Spacings for progressbars
        #self.param_pb_spacing_main = 2
        #self.param_pb_spacing_side = 4
        #self.param_text_limit = 256
        #self.param_max_text_size = 32
        self.params = DEFAULT_PARAMS.copy()
    
    def __getattr__(self, key):
        if key.startswith("param_"):
            return self.params[key[6:]]
        raise AttributeError("Unknown key %s" % key)

    def queue_text(self, text, x, y, scale=1):
        self.text_queue.append((text, x, y, scale))

    def render_node(self, node):
        if node.type in self.excludes:
            return
        #x, y = node.position
        #w, h = node.size
        self.drawer.add_rectangle(*node.position, *node.size, color=self.param_node_bg_color)
        self.drawer.add_line_rectangle(*node.position, node.size.x, node.size.y, color=self.param_node_border_color)

        if node.type == "progressbar":
            if node.size.x > node.size.y:
                self.drawer.add_rectangle(node.position.x+self.param_pb_spacing_main, node.position.y+self.param_pb_spacing_side, node.size.x*node.fraction-self.param_pb_spacing_main*2, node.size.y-self.param_pb_spacing_side*2, color=(1, 1, 1))
            else:
                self.drawer.add_rectangle(node.position.x+self.param_pb_spacing_side, node.position.y+self.param_pb_spacing_main, node.size.x-self.param_pb_spacing_side*2, node.size.y*node.fraction-self.param_pb_spacing_main*2, color=(1, 1, 1))

        
        if hasattr(node, "text"):
            if len(node.text) > self.param_text_limit: #TODO later
                text = node.text[:self.param_text_limit//2] + "..." + node.text[-self.param_text_limit//2:]
            else:
                text = node.text

            used_scale = min(node.size.y, self.param_max_text_size)
            size = self.font_render.calc_size(text, scale=used_scale)
            if size > 0 and size > node.size.x:
                used_scale *= node.size.x / size
                size = self.font_render.calc_size(text, scale=used_scale)

            align_ajust = node.size.x // 2 - size // 2
            if hasattr(node, "textalign"):
                if node.textalign == "left":
                    align_ajust = 0

            pos = MVec(node.position + node.size // 2)
            pos.x += align_ajust - node.size.x // 2
            text_height = self.font_render.calc_height(text, scale=used_scale)
            if text_height == 0:
                text_height = self.param_max_text_size
            pos.y += text_height // 2
            self.queue_text(text, *pos, scale=used_scale)

            if node.type == "textinput":
                cpos = node.position.x + self.font_render.calc_size(text[:node.cursor], scale=used_scale) + align_ajust
                cy = node.position.y+node.size.y/2
                txh = text_height / 2
                self.drawer.add_line((cpos, cy-txh), (cpos, cy+txh))

    def render(self):
        self.ctx.enable_only(moderngl.BLEND)
        self.text_queue.clear()
        queue = deque()
        queue.append(self.node)
        while queue:
            current = queue.popleft()
            self.render_node(current)
            for child in current.children:
                queue.append(child)
        matrix = Matrix4.orthogonal_projection(0, self.window.width, self.window.height, 0, -1, 1)
        self.drawer.render(mvp=matrix, change_context_state=False)
        for text in self.text_queue:
            self.font_render.render_string(*text, mvp=matrix, color=self.param_text_color)
            