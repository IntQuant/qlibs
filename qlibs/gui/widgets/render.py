from collections import deque

import moderngl

from ..basic_shapes import ShapeDrawer
from ...fonts.font_render import DirectFontRender
from ...fonts.font_search import find_reasonable_font
from ...math import Matrix4, MVec

class DefaultRenderer:
    def __init__(self, window, node, font=None, font_path=None):
        if font is None and font_path is None:
            font_path = find_reasonable_font()
        self.ctx = window.ctx
        self.font_render = DirectFontRender(self.ctx, font, font_path=font_path)
        self.drawer = ShapeDrawer(self.ctx)
        self.node = node
        self.window = window
        self.text_queue = []
        self.excludes = ["centerer"]
        self.drawer.default_z = -1
    
    def queue_text(self, text, x, y, scale=1):
        self.text_queue.append((text, x, y, scale))

    def render_node(self, node):
        if node.type in self.excludes:
            return
        self.drawer.add_rectangle(*node.position, *node.size, color=(1, 1, 1, 0.1))
        if node.type == "button":
            pos = MVec(node.position + node.size // 2)
            pos.x -= self.font_render.calc_size(node.text) // 2
            pos.y -= self.font_render.calc_height(node.text) // 2
            self.queue_text(node.text, *pos)

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
        matrix = Matrix4.orthogonal_projection(0, self.window.width, 0, self.window.height, -1, 1)
        self.drawer.render(mvp=matrix, change_context_state=False)
        for text in self.text_queue:
            self.font_render.render_string(*text, mvp=matrix)