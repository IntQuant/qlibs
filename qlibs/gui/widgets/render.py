from collections import deque
import warnings

import moderngl

from ..basic_shapes import ShapeDrawer
from ...fonts.font_render import DirectFontRender
from ...fonts.font_search import find_reasonable_font
from ...math import Matrix4, Vec2

DEFAULT_PARAMS = {
    "text_limit": 256,
    "max_text_size": 32,
    "pb_spacing_side": 4,
    "pb_spacing_main": 2,
    "node_bg_color": (0.1, 0.1, 0.1, 0.8),
    "node_border_color": (0.5, 0.5, 0.5, 0.8),
    "button_border_inactive_color": (0.5, 0.5, 0.25, 0.8),
    "button_border_hover_color": (0.5, 0.7, 0.7, 0.8),
    "button_border_active_color": (0.5, 1, 1, 0.8),
    "selectable_inactive_color": (0.5, 0.5, 0.3, 0.8),
    "selectable_active_color": (0.7, 1, 1, 0.8),
    "text_color": (1, 1, 1),
    "scrollbar_color": (1, 1, 1, 0.8),
    "progressbar_color": (1, 1, 1, 0.8),
}

OLD_DEFAULT_PARAMS = {
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

class DefaultRenderer:
    def __init__(self, window, node, font=None, font_path=None, font_render=None, is_selected_cb=None):
        if font is None and font_path is None:
            font_path = find_reasonable_font()
        self.ctx = window.ctx
        self.font_render = font_render or DirectFontRender(self.ctx, font, font_path=font_path)
        self.font_render.flip_y = True
        self.drawer = ShapeDrawer(self.ctx)
        self.node = node
        self.window = window
        self.text_queue = []
        self.excludes = ["centerer", "scrollablelist"]
        self.buttons = ["button", "togglebutton"]
        self.drawer.default_z = -1
        self.params = DEFAULT_PARAMS.copy()
        self.is_selected_cb = is_selected_cb
        self.matrix = None
        self.sprite_master = None
    
    def __getattr__(self, key):
        if key.startswith("param_"): #TODO - node-specific params
            return self.params[key[6:]]
        raise AttributeError("Unknown key %s" % key)

    def queue_text(self, text, x, y, scale=1):
        self.text_queue.append((text, x, y, scale))

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
            if node.image_mode == "fill":
                r = max(dx, dy)
            elif node.image_mode == "fit":
                r = min(dx, dy)
            else:
                warnings.warn("Node %s has invalid image mode %s" % (node, node.image_mode))
                
            dx /= r
            dy /= r

            pxz = 0.5 - dx*0.5
            pyz = 0.5 - dy*0.5
            pxo = 0.5 + dx*0.5
            pyo = 0.5 + dy*0.5

            tpoints = (
                (pxz, pyz), 
                (pxo, pyz), 
                (pxo, pyo), 
                (pxz, pyo),
            )
            
            self.sprite_master.add_sprite_rect(node.image_id, *node.position, *node.size, tpoints=tpoints)
        self.sprite_master.render(mvp=self.matrix)

    def render_node(self, node):
        if node.type in self.excludes and node.image_id is None:
            return
        if node.type == "customrender":
            self.render_drawer()
            node.render(
                Matrix4.orthogonal_projection(
                    node.position.x,
                    node.position.x+node.size.x,
                    node.position.y+node.size.y,
                    node.position.y,
                ),
            )
            return

        is_selected = node.selectable
        if self.is_selected_cb is not None:
            is_selected = self.is_selected_cb(node)

        if node.image_id is not None:
            self.render_image(node)
        else:
            self.drawer.add_rectangle(*node.position, *node.size, color=self.param_node_bg_color)

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
            self.drawer.add_line_rectangle(*node.position, node.size.x, node.size.y, color=self.param_node_border_color)

        if node.type == "progressbar":
            if node.size.x > node.size.y:
                self.drawer.add_rectangle(node.position.x+self.param_pb_spacing_main, node.position.y+self.param_pb_spacing_side, node.size.x*node.fraction-self.param_pb_spacing_main*2, node.size.y-self.param_pb_spacing_side*2, color=self.param_progressbar_color)
            else:
                self.drawer.add_rectangle(node.position.x+self.param_pb_spacing_side, node.position.y+self.param_pb_spacing_main, node.size.x-self.param_pb_spacing_side*2, node.size.y*node.fraction-self.param_pb_spacing_main*2, color=self.param_progressbar_color)

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

            pos = node.position + node.size // 2
            pos.x += align_ajust - node.size.x // 2
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

    def render(self):
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
        for text in self.text_queue:
            self.font_render.render_string(*text, mvp=self.matrix, color=self.param_text_color)
            