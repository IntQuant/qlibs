from array import array
import math

import moderngl

from ..math import Matrix4, IDENTITY
from ..resources.resource_manager import get_storage_of_context
from ..util import try_write

HALF_PI = math.pi / 2
QUART_PI = math.pi / 4

SHADER_VERTEX = "qlibs/shaders/sprite.vert"
SHADER_FRAGMENT = "qlibs/shaders/sprite.frag"


class SpriteDrawer:
    def __init__(self, ctx, size, data, components=4):
        self.ctx = ctx
        self.program = get_storage_of_context(self.ctx).get_program(SHADER_VERTEX, SHADER_FRAGMENT)
        self.texture = self.ctx.texture_array(size, components, data=data)
        self.size = size
        self.prepare()
        self.buffer = None
        self.vao = None
    
    def prepare(self):
        self.buffer_data = array("f")
    
    def add_sprite_rect(self, id_, x, y, w, h, z=0):
        data = [
            #First triangle
            x,   y,   0, 0, id_, z,
            x+w, y+h, 1, 1, id_, z,
            x+w, y,   1, 0, id_, z,
            #Second triangle
            x,   y,   0, 0, id_, z,
            x,   y+h, 0, 1, id_, z,
            x+w, y+h, 1, 1, id_, z,
        ]
        self.buffer_data.fromlist(data)
    
    def add_sprite_centered(self, id_, x, y, w, h, z=0):
        self.add_sprite_rect(id_, x - w//2, y - h//2, w, h, z)

    def add_sprite_rotated(self, id_, x, y, w, h, r, z=0):
        at = math.atan2(w, h)
        rot = r + math.pi
        d = math.sqrt(w*w + h*h) / 2

        sin = math.sin
        cos = math.cos

        point1 = x+sin(rot-at)*d,   y+cos(rot-at)*d
        point0 = x+sin(rot+at)*d, y+cos(rot+at)*d
        point3 = x+sin(rot+math.pi-at)*d, y+cos(rot+math.pi-at)*d
        point2 = x+sin(rot+math.pi+at)*d, y+cos(rot+math.pi+at)*d

        data = [
            #First triangle
            *point0,   0, 0, id_, z,
            *point2, 1, 1, id_, z,
            *point1,   1, 0, id_, z,
            #Second triangle
            *point0,   0, 0, id_, z,
            *point3, 0, 1, id_, z,
            *point2, 1, 1, id_, z,
        ]

        self.buffer_data.fromlist(data)

    def render(self, mvp=Matrix4(IDENTITY), reset=True):
        if len(self.buffer_data) == 0:
            return
        data = self.buffer_data.tobytes()
        if self.buffer is None or len(data) > self.buffer.size:
            if self.buffer is not None:
                self.buffer.release()
                self.vao.release()
            
            self.buffer = self.ctx.buffer(data)
            self.vao = self.ctx.simple_vertex_array(self.program, self.buffer, "pos", "tpos", "z")

        else:
            self.buffer.write(data)
        self.texture.use()
        try_write(self.program, "mvp", mvp.bytes())
        self.vao.render(moderngl.TRIANGLES, vertices=len(self.buffer_data)//4) #TODO: test this
        if reset:
            self.prepare()
        
    
    def write_layer(self, id_, data):
        text = self.texture
        viewport = (0, 0, id_, text.width, text.height, 1)
        text.write(data, viewport)

    def __del__(self):
        self.texture.release()
        if self.buffer is not None:
            self.buffer.release()
        if self.vao is not None:
            self.vao.release()