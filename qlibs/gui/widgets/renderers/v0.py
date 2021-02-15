from collections import deque
import warnings

import moderngl

from ...basic_shapes import ShapeDrawer
from ....fonts.font_render import DirectFontRender, FormattedText
from ....math import Matrix4, Vec2


V0_PARAMS_V3 = {
    "text_limit": 256,
    "max_text_size": 32,
    "pb_spacing_side": 4,
    "pb_spacing_main": 2,
    "node_bg_color": (0.1, 0.1, 0.1, 1),
    "text_node_bg_color": (0.05, 0.05, 0.05, 1),
    "node_border_color": (0.2, 0.2, 0.2, 1),
    "button_border_inactive_color": (0.5, 0.5, 0.5, 1),
    "button_border_hover_color": (0.5, 0.7, 0.7, 0.8),
    "button_border_active_color": (0.5, 1, 1, 0.8),
    "selectable_inactive_color": (0.2, 0.2, 0.2, 1),
    "selectable_active_color": (0.7, 1, 1, 0.8),
    "text_color": (1, 1, 1),
    "scrollbar_color": (1, 1, 1, 0.8),
    "progressbar_color": (1, 1, 1, 0.8),
    "img_flip": True,
}

V0_PARAMS_V1 = {
    "text_limit": 256,
    "max_text_size": 32,
    "pb_spacing_side": 4,
    "pb_spacing_main": 2,
    "node_bg_color": (1, 1, 1, 0.1),
    "node_border_color": (1, 1, 1, 0.2),
    "button_border_inactive_color": (1, 1, 0.5, 0.4),
    "button_border_hover_color": (0.5, 1, 1, 0.6),
    "button_border_active_color": (0.5, 1, 1, 0.7),
    "selectable_inactive_color": (1, 1, 0.6, 0.3),
    "selectable_active_color": (0.7, 1, 1, 0.7),
    "text_color": (1, 1, 1),
    "scrollbar_color": (1, 1, 1, 0.8),
    "progressbar_color": (1, 1, 1, 0.8),
}

class V0Renderer:
    def __init__(self, window, node=None, font=None, font_path=None, font_render=None, is_selected_cb=None):
        if font is not None or font_path is not None:
            warnings.warn("font and font_path are not supported anymore", category=DeprecationWarning)
        self.ctx = window.ctx
        self.font_render = font_render or DirectFontRender(self.ctx, font, font_path=font_path)
        self.font_render.flip_y = True
        self.drawer = ShapeDrawer(self.ctx)
        self.node = node
        self.window = window
        self.text_queue = []
        self.excludes = ["centerer", "scrollablelist"]
        self.buttons = ["button", "togglebutton", "radiobutton"]
        self.border_excludes = ["node", "textnode", "textinput"]
        self.drawer.default_z = -1
        self.params = V0_PARAMS_V3.copy()
        self.is_selected_cb = is_selected_cb
        self.matrix = None
        self.sprite_master = None
        self.image_ident = 0
    
    def __getattr__(self, key):
        if key.startswith("param_"): #TODO - node-specific params
            return self.params[key[6:]]
        raise AttributeError("Unknown key %s" % key)

    def queue_text(self, text, x, y, scale=1, multiline=False, scissor_params=None):
        self.text_queue.append((text, x, y, scale, scissor_params, multiline))

    def render_image(self, node):
        self.render_drawer()
        #print("Rendering", node.image_id, "at", node.pos)
        if node.image_mode is None:
            self.sprite_master.add_sprite_rect(node.image_id, *node.position, *node.size)
        else:
            
            dx = 1
            ratio = node.size.y / node.size.x
            dy = dx*node.image_ratio*ratio
            
            r = 1    
            if node.image_mode.startswith("fill"):
                r = min(dx, dy)
            elif node.image_mode.startswith("fit"):
                r = max(dx, dy)
            else:
                warnings.warn("Node %s has invalid image mode %s" % (node, node.image_mode))
                
            dx /= r
            dy /= r

            cpos = node.position + node.size/2

            sizey = node.size.y*dx
            if self.param_img_flip:
                sizey *= -1

            if node.image_mode.endswith("cleft"):
                x = node.position.x + node.size.x*dy * 0.5
                y = node.position.y + node.size.y*dx * 0.5
                self.image_ident = node.size.x*dy + 1
                self.sprite_master.add_sprite_centered(node.image_id, x, y, node.size.x*dy, sizey)
            else:
                self.sprite_master.add_sprite_centered(node.image_id, *cpos, node.size.x*dy, node.size.y*dx)# tpoints=tpoints)
        self.sprite_master.render(mvp=self.matrix)

    def render_node(self, node):
        self.image_ident = 0
        if node.hidden:
            return
        if node.type in self.excludes and node.image_id is None:
            return
        if node.type == "customrender":
            self.render_drawer()
            #mvp = Matrix4.orthogonal_projection(
            #    node.position.x,
            #    node.position.x+node.size.x,
            #    node.position.y+node.size.y,
            #    node.position.y,
            #)
            bak = self.ctx.viewport
            try:
                self.ctx.viewport = (node.position.x, node.position.y, node.size.x, node.size.y)
                node.ctx = self.ctx
                node.render(node)
            finally:
                self.ctx.viewport = bak
            return

        is_selected = node.selectable
        if self.is_selected_cb is not None:
            is_selected = self.is_selected_cb(node)

        if node.image_id is not None:
            self.render_image(node)
        else:
            if node.type == "textinput":
                color = self.param_text_node_bg_color
            else:
                color = self.param_node_bg_color
            self.drawer.add_rectangle(*node.position, *node.size, color=color)

        if node.type in self.buttons:
            active = getattr(node, "state", getattr(node, "pressed", False))
            hovered = getattr(node, "hovered", False)
            if active:
                color = self.param_button_border_active_color
            elif hovered:
                color = self.param_button_border_hover_color
            else:
                color = self.param_button_border_inactive_color
            self.drawer.add_line_rectangle(*node.position, node.size.x, node.size.y, color=color)
        elif node.selectable:
            if is_selected:
                color = self.param_selectable_active_color
            else:
                color = self.param_selectable_inactive_color
            self.drawer.add_line_rectangle(*node.position, node.size.x, node.size.y, color=color)
        else:
            if node.type not in self.border_excludes:
                self.drawer.add_line_rectangle(*node.position, node.size.x, node.size.y, color=self.param_node_border_color)

        if node.type == "progressbar":
            if node.size.x > node.size.y:
                self.drawer.add_rectangle(node.position.x+self.param_pb_spacing_main, node.position.y+self.param_pb_spacing_side, (node.size.x-self.param_pb_spacing_main*2)*node.fraction, node.size.y-self.param_pb_spacing_side*2, color=self.param_progressbar_color)
            else:
                self.drawer.add_rectangle(node.position.x+self.param_pb_spacing_side, node.position.y+self.param_pb_spacing_main, node.size.x-self.param_pb_spacing_side*2, (node.size.y-self.param_pb_spacing_side*2)*node.fraction, color=self.param_progressbar_color)

        if node.type == "scrollbar":
            if node.direction == 1:
                pos_x = node.position.x
                size_x = node.size.x
                pos_y = node.position.y + node.size.y * node.pos * 0.9
                size_y = node.size.y * 0.1
            else:
                pos_y = node.position.y
                size_y = node.size.y
                pos_x = node.position.x + node.size.x * node.pos * 0.9
                size_x = node.size.x * 0.1
            self.drawer.add_rectangle(pos_x, pos_y, size_x, size_y, color=self.param_scrollbar_color)
        
        if hasattr(node, "text"):
            if node.type == "text" or isinstance(node.text, FormattedText):
                pos = Vec2(*node.position)
                pos.y = self.window.height - pos.y - node.size.y
                scissor = (*pos, *node.size)
                self.queue_text(node.text, node.position.x+4, node.position.y+node.scale, node.scale, multiline=node.size.x-8, scissor_params=scissor)
            else:
                
                if len(node.text) > self.param_text_limit: #TODO later
                    text = node.text[:self.param_text_limit//2] + "..." + node.text[-self.param_text_limit//2:]
                else:
                    text = node.text

                used_scale = min(node.size.y, self.param_max_text_size)
                ident = 8
                size = self.font_render.calc_size(text, scale=used_scale)
                if size > 0 and size > node.size.x - self.image_ident - ident:
                    used_scale *= (node.size.x-self.image_ident-ident) / size
                    size = self.font_render.calc_size(text, scale=used_scale)

                align_ajust = node.size.x // 2 - size // 2
                if hasattr(node, "textalign"):
                    if node.textalign == "left":
                        align_ajust = ident / 2

                pos = node.position + node.size // 2
                pos.x += self.image_ident + align_ajust - node.size.x // 2
                text_height = self.font_render.calc_height(text, scale=used_scale)
                if text_height == 0:
                    text_height = self.param_max_text_size
                pos.y += text_height // 2
                self.queue_text(text, *pos, scale=used_scale)

                if node.type == "textinput":
                    if is_selected: #Draw cursor
                        cpos = node.position.x + self.font_render.calc_size(text[:node.cursor], scale=used_scale) + align_ajust
                        cy = node.position.y+node.size.y/2
                        txh = text_height / 2
                        self.drawer.add_line((cpos, cy-txh), (cpos, cy+txh))

    def render_drawer(self):
        self.drawer.render(mvp=self.matrix, change_context_state=False)

    def render(self, node):
        self.node = node
        try:
            self.ctx.enable_only(moderngl.BLEND)
            self.text_queue.clear()
            self.matrix = Matrix4.orthogonal_projection(0, self.window.width, self.window.height, 0, -1, 1)
            queue = deque()
            queue.append(self.node)
            while queue:
                current = queue.pop()
                self.render_node(current)
                for child in current.children:
                    queue.append(child)
            self.render_drawer()
            
            for text_data in self.text_queue:
                *text, scissor, multiline = text_data
                if not multiline:
                    self.font_render.render_string(*text, mvp=self.matrix, color=self.param_text_color)
                else:
                    self.ctx.scissor = scissor
                    self.font_render.render_multiline(*text[:3], multiline, mvp=self.matrix)
                    self.ctx.scissor = None
        finally:
            self.ctx.scissor = None
            