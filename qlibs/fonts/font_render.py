"""
  Module for rendering text
"""

from array import array

import freetype

from ..resources.resource_manager import get_storage_of_context
from ..math.vec import IVec
from ..math.matrix import Matrix4, IDENTITY
from ..util import try_write

import moderngl

class Glyph:
    """
      Class for storing glyph data: *advance*, *size*, *bearing*, and opengl *texture*
    """
    def __init__(self, ctx, glyph):
        """
        Initialize everything from glyph
        """
        self.advance = IVec(glyph.advance.x, glyph.advance.y)
        self.size = IVec(glyph.bitmap.width, glyph.bitmap.rows)
        self.bearing = IVec(glyph.bitmap_left, glyph.bitmap_top)
        data = glyph.bitmap.buffer
        self.texture = ctx.texture(tuple(self.size), 1, bytes(data), dtype="f1", alignment=1)
        self.texture.repeat_x = False
        self.texture.repeat_y = False


class DirectFontRender:
    """
      Render text using font
    """
    def __init__(self, ctx, font: freetype.Face, font_path=None):
        """
        *ctx* is a moderngl context
        *font_path* will be used if *font* is None
        """
        self.ctx = ctx
        self.font = font or freetype.Face(font_path)
        self.font.set_pixel_sizes(0, 48)
        self.cache = dict()
        self.program = get_storage_of_context(ctx).get_program("qlibs/shaders/text.vert", "qlibs/shaders/text.frag")
        self.vao = None
    
    def get_glyph(self, char):
        glyph = self.cache.get(char, None)
        if glyph is None:
            self.font.load_char(char)
            glyph = Glyph(self.ctx, self.font.glyph)
            self.cache[char] = glyph
        return glyph

    def render_string(self, text, x, y, scale=1, color=(1, 1, 1), mvp=Matrix4(IDENTITY), enable_blending=True):
        """
        Render text with given parameters
        """
        if enable_blending:
            self.ctx.enable_only(moderngl.BLEND)
        
        pos = IVec(x, y)
        try_write(self.program, "mvp", mvp.bytes())
        try_write(self.program, "text_color", IVec(color).bytes())
        for char in text:
            glyph = self.get_glyph(char) 
            glyph.texture.use()
            h = glyph.size.y * scale
            w = glyph.size.x * scale
            
            posy = pos.y - (glyph.size.y - glyph.bearing.y) * scale
            
            data = array("f", (
                pos.x, posy + h, 0, 0,
                pos.x, posy, 0, 1,
                pos.x + w, posy, 1, 1,
                pos.x, posy + h, 0, 0,
                pos.x + w, posy, 1, 1,
                pos.x + w, posy + h, 1, 0
            ))
            
            if self.vao is None:
                self.buffer = self.ctx.buffer(data)
                self.vao = self.ctx.simple_vertex_array(
                    self.program, self.buffer, "pos", "tex"
                )
            else:
                self.buffer.write(data)    
            self.vao.render()
            pos += glyph.advance * (scale / 64)

    def calc_size(self, text):
        x = 0
        for char in text:
            x += self.get_glyph(char).advance.x
        return x / 64
    
    def calc_height(self, text, full=False):
        max_y = 0
        min_y = 0
        for char in text:
            glyph = self.get_glyph(char)
            max_y = max(max_y, glyph.size.y)
            if full:
                min_y = min(min_y, -glyph.size.y - glyph.bearing.y)
        return abs(max_y - min_y)

    