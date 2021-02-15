"""
  Module for rendering text
"""

from array import array
from functools import lru_cache
import warnings
from qlibs.fonts import font_loader, font_search
from typing import Text
import weakref
from enum import Enum, auto

import freetype
import moderngl

from ..resources.resource_manager import get_storage_of_context
from ..math.vec import IVec, Vec2
from ..math.matrix import Matrix4, IDENTITY
from ..util import try_write
from ..gui.window import current_context

global_cache = weakref.WeakValueDictionary()

class TextAlign(Enum):
    LEFT = auto()
    CENTER = auto()

class FormattedTextToken(Enum):
    LINEBREAK = auto()


class FormattingData(dict):
    def __getattr__(self, name):
        return self[name]
    
    def copy(self):
        return FormattingData(**self)


class FormattedText:
    def __init__(self, text=None, tokens=None, **kwargs):
        self.tokens = tokens or list()
        if kwargs:
            self.tokens.insert(0, FormattingData(**kwargs))
        if text is not None:
            self.parse(text)

    def parse(self, text):
        for line in text.splitlines():
            self.tokens.extend(line.split())
            self.tokens.append(FormattedTextToken.LINEBREAK)


class GGlyph:
    """
      Class for storing glyph data: *advance*, *size*, *bearing*, and opengl *texture*
    """
    __slots__ = ("advance", "size", "bearing", "texture", "__weakref__")
    def __init__(self, ctx, glyph):
        """
        Initialize everything from glyph
        """
        self.advance = Vec2(glyph.advance.x, glyph.advance.y)
        self.size = Vec2(glyph.bitmap.width, glyph.bitmap.rows)
        self.bearing = Vec2(glyph.bitmap_left, glyph.bitmap_top)
        data = glyph.bitmap.buffer
        self.texture = ctx.texture(tuple(self.size), 1, bytes(data), dtype="f1", alignment=1)
        self.texture.repeat_x = False
        self.texture.repeat_y = False

    def __del__(self):
        self.texture.release()


class DirectFontRender:
    """
      Render text using font
    """
    def __init__(self, ctx=None, font=None, font_path=None, pixel_size=48, flip_y=False, default_font="default"):
        """
        *ctx* is a moderngl context.
        *font_path* and *font* are deprecated and ignored.
        *default_font* - name of default font.
        """
        ctx = ctx or current_context.get()
        if font is not None or font_path is not None:
            warnings.warn("font and font_path are not supported anymore", category=DeprecationWarning)
        self.ctx = ctx
        self.font = default_font
        self.pixel_size = pixel_size
        self.cache = dict()
        self.program = get_storage_of_context(ctx).get_program("qlibs/shaders/text.vert", "qlibs/shaders/text.frag")
        self.vao = None
        self.buffer = None
        self.flip_y = flip_y
    
    def get_glyph(self, char, font_name=None):
        font_name = font_name or self.font
        glyph = self.cache.get(char, None)
        global_key = (font_name, id(self.ctx), self.pixel_size, char)
        if glyph is None:
            try:
                glyph = global_cache[global_key]
            except KeyError:
                glyph = None
        if glyph is None:
            glyph = GGlyph(self.ctx, font_loader.font_loader.get().get(font_name, char))
            self.cache[char] = glyph
            global_cache[global_key] = glyph
        return glyph

    def render_string(self, text, x, y, scale=1, color=(1, 1, 1), mvp=Matrix4(IDENTITY), enable_blending=True, font=None, **kwargs):
        """
        Render text with given parameters
        """
        if enable_blending:
            self.ctx.enable_only(moderngl.BLEND)
        
        if len(color) != 3:
            raise ValueError("Invalid color - len 3 required")

        scale /= self.pixel_size

        pos = Vec2(x, y)
        try_write(self.program, "mvp", mvp.bytes())
        try_write(self.program, "text_color", IVec(color).bytes())
        for char in text:
            glyph = self.get_glyph(char, font_name=font) 
            glyph.texture.use()
            h = glyph.size.y * scale
            w = glyph.size.x * scale
            
            if self.flip_y:
                posy = pos.y - glyph.bearing.y*scale
            else:
                posy = pos.y - (glyph.size.y - glyph.bearing.y) * scale
            
            if self.flip_y:
                data = array("f", (
                    pos.x, posy + h, 0, 1,
                    pos.x, posy, 0, 0,
                    pos.x + w, posy, 1, 0,
                    pos.x, posy + h, 0, 1,
                    pos.x + w, posy, 1, 0,
                    pos.x + w, posy + h, 1, 1
                ))
            else:
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

    def render_multiline(self, text, x, y, max_line_len, *, scale=32, vertical_advance=None, min_sep=15, **kwargs):
        if not isinstance(text, FormattedText):
            ftext = FormattedText()
            ftext.parse(text)
        else:
            ftext = text
        
        formatting_data = FormattingData(align=TextAlign.LEFT, **kwargs)
        words = list(ftext.tokens)
        
        i = -1
        line = list()
        cur_line_len = 0
        words.reverse()
        cy = y
        if vertical_advance is None:
            vertical_advance = scale * (1 if self.flip_y else -1)
        while words:
            is_word = isinstance(words[-1], str)
            if is_word:
                word_len = self.calc_size(words[-1], scale)
            else:
                word_len = 0
            finish_line = word_len + cur_line_len > max_line_len
            if is_word and (word_len + cur_line_len <= max_line_len or cur_line_len == 0):
                cur_line_len += word_len + min_sep
                line.append((words.pop(), formatting_data))
            if not is_word:
                token = words.pop()
                if token is FormattedTextToken.LINEBREAK:
                    finish_line = True
                if isinstance(token, FormattingData):
                    formatting_data = formatting_data.copy()
                    formatting_data.update(token)

            if finish_line or not words:
                if formatting_data.align is TextAlign.CENTER:
                    cx = x + (max_line_len - cur_line_len + min_sep) // 2
                else:
                    cx = x
                for word, formatting in line:
                    self.render_string(word, cx, cy, scale=scale, **formatting)
                    cx += self.calc_size(word, scale=scale) + min_sep
                line.clear()
                cur_line_len = 0
                cy += vertical_advance
            
    @lru_cache(1024)
    def calc_size(self, text, scale=1):
        x = 0
        for char in text:
            x += self.get_glyph(char).advance.x
        return x / 64 * scale / self.pixel_size
    
    @lru_cache(1024)
    def calc_height(self, text, scale=1, full=False):
        max_y = 0
        min_y = 0
        for char in text:
            glyph = self.get_glyph(char)
            max_y = max(max_y, glyph.bearing.y)
            if full:
                min_y = min(min_y, -glyph.size.y - glyph.bearing.y)
        return abs(max_y - min_y) * scale / self.pixel_size

    def __del__(self):
        if self.vao:
            self.vao.release()
        if self.buffer:
            self.buffer.release()