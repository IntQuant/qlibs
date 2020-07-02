"""
  Sprite drawer. Uses texture atlas to draw images.

  Low level. Consider using qlibs.highlevel.graphics instead.
"""

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

TEXTURE_POINTS = ((0, 0), (1, 0), (1, 1), (0, 1))

import logging
logger = logging.getLogger("qlibs.gui.sprite_drawer")

class SpriteDrawerBase:
    def __init__(self, texture, program, ctx):
        self.texture = texture
        self.program = program
        self.ctx = ctx
        self.buffer = None
        self.vao = None
        self.prepare()
    
    def prepare(self):
        self.buffer_data = array("f")
    
    def add_sprite_rect(self, id_, x, y, w, h, z=0, color=(1, 1, 1, 1), tpoints=TEXTURE_POINTS):
        data = [
            #First triangle
            x,   y,   *tpoints[0], id_, z, *color,
            x+w, y+h, *tpoints[2], id_, z, *color,
            x+w, y,   *tpoints[1], id_, z, *color,
            #Second triangle
            x,   y,   *tpoints[0], id_, z, *color,
            x,   y+h, *tpoints[3], id_, z, *color,
            x+w, y+h, *tpoints[2], id_, z, *color,
        ]
        self.buffer_data.fromlist(data)
    
    def add_sprite_centered(self, id_, x, y, w, h, z=0, color=(1, 1, 1, 1), tpoints=TEXTURE_POINTS):
        self.add_sprite_rect(id_, x - w/2, y - h/2, w, h, z, color, tpoints)

    def add_sprite_rotated(self, id_, x, y, w, h, r, z=0, color=(1, 1, 1, 1), tpoints=TEXTURE_POINTS):
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
            *point0, *tpoints[0], id_, z, *color,
            *point2, *tpoints[2], id_, z, *color,
            *point1, *tpoints[1], id_, z, *color,
            #Second triangle
            *point0, *tpoints[0], id_, z, *color,
            *point3, *tpoints[3], id_, z, *color,
            *point2, *tpoints[2], id_, z, *color,
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
            self.vao = self.ctx.simple_vertex_array(self.program, self.buffer, "pos", "tpos", "z", "tint")
        else:
            self.buffer.write(data)
        self.texture.use()
        try_write(self.program, "mvp", mvp.bytes())
        self.vao.render(moderngl.TRIANGLES, vertices=len(self.buffer_data)//10) #TODO: test this
        if reset:
            self.prepare()

    def clear(self):
        self.prepare()

    def __del__(self):
        if self.buffer is not None:
            self.buffer.release()
        if self.vao is not None:
            self.vao.release()


class Sprite:
    def __init__(self, location, owner, id_, x, y, w, h, r, z, color):
        self._location = location
        self.owner = owner
        self.id_, self.x, self.y, self.w, self.h, self.r, self.z = id_, x, y, w, h, r, z
        self.color = color
    
    def update(self):
        id_, x, y, w, h, r, z = self.id_, self.x, self.y, self.w, self.h, self.r, self.z
        
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
            *point0,   0, 0, id_, z, *self.color,
            *point2, 1, 1, id_, z, *self.color,
            *point1,   1, 0, id_, z, *self.color,
            #Second triangle
            *point0,   0, 0, id_, z, *self.color,
            *point3, 0, 1, id_, z, *self.color,
            *point2, 1, 1, id_, z, *self.color,
        ]
        self.owner.update_location(self._location, data)

    def remove(self):
        self.owner.remove_location(self._location)

class ObjectDrawer():
    """
      Untested
    """
    def __init__(self, texture, program, ctx):
        self.texture = texture
        self.program = program
        self.buffer = None
        self.vao = None
        self.sprites = dict()
        self.verticle_size = 10
        self.vertices_per_object = 6
        self.ctx = ctx
    
    @property
    def object_count(self):
        return len(self.sprites)

    def calc_buffer_size(self):
        return (2**(self.object_count.bit_length()+1)) * self.verticle_size * self.vertices_per_object

    def assert_buffer(self):
        target_size = self.calc_buffer_size()
        if self.buffer is None or target_size > self.buffer.size:
            logger.debug("Reallocating buffer")
            new_buffer = self.ctx.buffer(reserve=target_size)
            if self.buffer is not None:
                self.ctx.copy_buffer(self.buffer, new_buffer)
                
                self.buffer.release()
                self.vao.release()
            
            self.buffer = new_buffer
            self.vao = self.ctx.simple_vertex_array(self.program, self.buffer, "pos", "tpos", "z", "tint")

    def render(self, mvp=Matrix4(IDENTITY)):
        self.texture.use()
        try_write(self.program, "mvp", mvp.bytes())
        self.vao.render(moderngl.TRIANGLES, vertices=self.object_count*self.vertices_per_object)
    
    def add_sprite(self, id_, x, y, w, h, r=0, z=0, color=(1, 1, 1, 1)):
        spr = Sprite(self.object_count, self, id_, x, y, w, h, r, z, color)
        self.sprites[spr._location] = spr
        spr.update()
        return spr

    def update_location(self, location, data):
        self.assert_buffer()
        db = bytes(array("f", data))
        print(len(db), self.buffer.size)
        self.buffer.write(db, offset=location*len(db))

    def remove_location(self, location):
        self.sprites[location] = self.sprites[self.object_count-1]
        self.sprites[location]._location = location
        self.sprites[location].update()

    def __del__(self):
        if self.buffer is not None:
            self.buffer.release()
        if self.vao is not None:
            self.vao.release()


class SpriteDrawer(SpriteDrawerBase):
    def __init__(self, ctx, size, data, components=4, program=None):
        self.ctx = ctx
        self.program = program or get_storage_of_context(self.ctx).get_program(SHADER_VERTEX, SHADER_FRAGMENT)
        self.texture = self.ctx.texture_array(size, components, data=data)
        self.texture.repeat_x = False
        self.texture.repeat_y = False
        self.size = size
        self.prepare()
        self.buffer = None
        self.vao = None
    
    def write_layer(self, id_, data):
        text = self.texture
        viewport = (0, 0, id_, text.width, text.height, 1)
        text.write(data, viewport)

    def fork(self):
        """
          Create another sprite drawer. It will share texture but not buffers
        """
        return SpriteDrawerBase(self.texture, self.program, self.ctx)

    def fork_object_mode(self):
        return ObjectDrawer(self.texture, self.program, self.ctx)

    def __del__(self):
        self.texture.release()
        if self.buffer is not None:
            self.buffer.release()
        if self.vao is not None:
            self.vao.release()