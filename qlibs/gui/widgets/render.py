from collections import deque

import moderngl

from ..basic_shapes import ShapeDrawer
from ...fonts.font_render import DirectFontRender
from ...fonts.font_search import find_reasonable_font
from ...math import Matrix4, MVec

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
        self.pbspcm = 2
        self.pbspcs = 4
        self.text_limit = 256
        self.max_text_size = 32
    
    def queue_text(self, text, x, y, scale=1):
        self.text_queue.append((text, x, y, scale))

    def render_node(self, node):
        if node.type in self.excludes:
            return
        #x, y = node.position
        #w, h = node.size
        self.drawer.add_rectangle(*node.position, *node.size, color=(1, 1, 1, 0.1))
        
        if node.type == "progressbar":
            if node.size.x > node.size.y:
                self.drawer.add_rectangle(node.position.x+self.pbspcm, node.position.y+self.pbspcs, node.size.x*node.fraction-self.pbspcm*2, node.size.y-self.pbspcs*2, color=(1, 1, 1))
            else:
                self.drawer.add_rectangle(node.position.x+self.pbspcs, node.position.y+self.pbspcm, node.size.x-self.pbspcs*2, node.size.y*node.fraction-self.pbspcm*2, color=(1, 1, 1))

        
        if hasattr(node, "text"):
            if len(node.text) > self.text_limit: #TODO later
                text = node.text[:self.text_limit//2] + "..." + node.text[-self.text_limit//2:]
            else:
                text = node.text

            

            used_scale = min(node.size.y, self.max_text_size)
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
            pos.y += self.font_render.calc_height(text, scale=used_scale) // 2
            self.queue_text(text, *pos, scale=used_scale)

            if node.type == "textinput":
                cpos = node.position.x + self.font_render.calc_size(text[:node.cursor], scale=used_scale) + align_ajust
                
                self.drawer.add_line((cpos, node.position.y), (cpos, node.position.y+node.size.y))

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
            self.font_render.render_string(*text, mvp=matrix)
            