"""
  Module for rendering text
"""

from array import array
from collections import deque
from functools import lru_cache
from html.parser import HTMLParser
import itertools
import warnings
from qlibs.fonts import font_loader
import weakref
from enum import Enum, auto

import moderngl

from ..resources.resource_manager import get_storage_of_context
from ..math.vec import IVec, Vec2
from ..math.matrix import Matrix4, IDENTITY
from ..util import try_write
from ..gui.window import current_context

SCALE_SAFETY_MARGIN = 8

global_cache = weakref.WeakValueDictionary()

class TextAlign(Enum):
    LEFT = auto()
    CENTER = auto()

class FormattedTextToken(Enum):
    LINEBREAK = auto()
    POP_FORMAT = auto()


class FormattingData(dict):
    def __getattr__(self, name):
        return self.get(name, None)
    
    def copy(self):
        return FormattingData(**self)


class HTMLFormatParser(HTMLParser):
    CDATA_CONTENT_ELEMENTS = ("raw",)
    def __init__(self, color_converter):
        super().__init__()
        self.result = []
        self._color_converter = color_converter
        self._is_raw = False
    
    def handle_starttag(self, tag: str, attrs):
        attrs = {k: v for (k, v) in attrs}
        if tag == "br":
            self.result.append(FormattedTextToken.LINEBREAK)
        elif tag == "style":
            fmt = FormattingData()
            if "color" in attrs:
                color_str = attrs["color"]
                if color_str.startswith("#"):
                    color_val = int(color_str[1:], base=16)
                    r = (color_val & 0xFF0000) / 0xFF0000
                    g = (color_val & 0x00FF00) / 0x00FF00
                    b = (color_val & 0x0000FF) / 0x0000FF
                    fmt["color"] = (r, g, b)
                else:
                    if self._color_converter is not None:
                        fmt["color"] = self._color_converter(color_str)
                    else:
                        raise ValueError(f"Unknown color '{color_str}'")
            if "font" in attrs:
                fmt["font"] = attrs["font"]
            self.result.append(fmt)
        elif tag == "raw":
            self._is_raw = True
    
    def handle_data(self, data: str) -> None:
        if self._is_raw:
            self.result.append(data)
        else:
            self.result.extend(data.split())
    
    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self.result.append(FormattedTextToken.POP_FORMAT)
        elif tag == "raw":
            self._is_raw = False



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
    
    @classmethod
    def from_html(cls, text, color_converter=None):
        parser = HTMLFormatParser(color_converter)
        parser.feed(text)
        return cls(tokens=parser.result)


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
        #self.texture.build_mipmaps()
        self.texture.repeat_x = False
        self.texture.repeat_y = False

    def __del__(self):
        self.texture.release()


class DirectFontRender:
    """
      Render text using font
    """
    def __init__(self, ctx=None, font=None, font_path=None, pixel_size=48, flip_y=False, default_font="default", adaptive_pixel_size=True, base_pixel_size=8):
        """
        *ctx* is a moderngl context.
        *font_path* and *font* are deprecated and ignored.
        *default_font* - name of default font.
        *adaptive_pixel_size* - whether to use different glyph sizes or not. True results in better performance.
        """
        ctx = ctx or current_context.get()
        if font is not None or font_path is not None:
            warnings.warn("font and font_path are not supported anymore", category=DeprecationWarning)
        self.ctx = ctx
        self.font = default_font
        self.base_pixel_size = base_pixel_size
        self.pixel_size = pixel_size
        self.adaptive_pixel_size = adaptive_pixel_size
        self.cache = dict()
        self._last_added_to_cache = deque()
        self.max_cache_size = 256
        self.program = get_storage_of_context(ctx).get_program("qlibs/shaders/text.vert", "qlibs/shaders/text.frag")
        self.vao = None
        self.buffer = None
        self.flip_y = flip_y
    
    def get_glyph(self, char, font_name=None):
        font_name = font_name or self.font
        global_key = (font_name, id(self.ctx), self.pixel_size, char)
        glyph = self.cache.get(global_key, None)
        if glyph is None:
            try:
                glyph = global_cache[global_key]
            except KeyError:
                glyph = None
        if glyph is None:
            glyph = GGlyph(self.ctx, font_loader.font_loader.get().get(font_name, char, pixel_size=self.pixel_size))
            self._last_added_to_cache.append(global_key)
            self.cache[global_key] = glyph
            while len(self.cache) > self.max_cache_size:
                del self.cache[self._last_added_to_cache.popleft()]
            global_cache[global_key] = glyph
        return glyph
    
    def get_kerning(self, left_char, right_char, font_name=None):
        font_name = font_name or self.font
        return font_loader.font_loader.get().get_kerning(font_name, left_char, right_char, pixel_size=self.pixel_size)

    def render_string(self, text, x, y, scale=1, color=(1, 1, 1), mvp=Matrix4(IDENTITY), enable_blending=True, font=None, kerning_enabled=True, **kwargs):
        """
        Render text with given parameters
        """
        if self.adaptive_pixel_size:
            #We always want to have a bit bigger texture for safety, so we add SCALE_SAFETY_MARGIN to scale
            larger_power_of_two = 2**max(8, int(scale+SCALE_SAFETY_MARGIN)).bit_length()
            self.pixel_size = max(larger_power_of_two, self.base_pixel_size)

        if enable_blending:
            self.ctx.enable_only(moderngl.BLEND)
        
        if len(color) != 3:
            raise ValueError("Invalid color - len 3 required")

        scale /= self.pixel_size

        pos = Vec2(x, y)
        try_write(self.program, "mvp", mvp.bytes())
        try_write(self.program, "text_color", IVec(color).bytes())
        for char, next_char in itertools.zip_longest(text, text[1:]):
            glyph = self.get_glyph(char, font_name=font) 
            glyph.texture.use()
            h = glyph.size.y * scale
            w = glyph.size.x * scale
            
            if self.flip_y:
                posy = pos.y - glyph.bearing.y*scale
            else:
                posy = pos.y - (glyph.size.y - glyph.bearing.y) * scale
            
            x_shift = glyph.bearing.x * scale

            if self.flip_y:
                data = array("f", (
                    pos.x + x_shift, posy + h, 0, 1,
                    pos.x + x_shift, posy, 0, 0,
                    pos.x + x_shift + w, posy, 1, 0,
                    pos.x + x_shift, posy + h, 0, 1,
                    pos.x + x_shift + w, posy, 1, 0,
                    pos.x + x_shift + w, posy + h, 1, 1
                ))
            else:
                data = array("f", (
                    pos.x + x_shift, posy + h, 0, 0,
                    pos.x + x_shift, posy, 0, 1,
                    pos.x + x_shift + w, posy, 1, 1,
                    pos.x + x_shift, posy + h, 0, 0,
                    pos.x + x_shift + w, posy, 1, 1,
                    pos.x + x_shift + w, posy + h, 1, 0
                ))
            
            if self.vao is None:
                self.buffer = self.ctx.buffer(data)
                self.vao = self.ctx.simple_vertex_array(
                    self.program, self.buffer, "pos", "tex"
                )
            else:
                self.buffer.write(data)    
            self.vao.render()
            if kerning_enabled and next_char is not None:
                kerning = self.get_kerning(char, next_char, font_name=font)
            else:
                kerning = Vec2(0, 0)
            pos += (glyph.advance + kerning) * (scale / 64)

    def render_multiline(self, text, x, y, max_line_len, *, scale=32, vertical_advance=None, min_sep=15, **kwargs):
        if not isinstance(text, FormattedText):
            ftext = FormattedText()
            ftext.parse(text)
        else:
            ftext = text
        
        min_sep *= scale/32
        formatting_data = FormattingData(align=TextAlign.LEFT, **kwargs)
        words = list(ftext.tokens)

        line = list()
        cur_line_len = 0
        words.reverse()
        cy = y
        format_stack = list()
        if vertical_advance is None:
            vertical_advance = scale * (1 if self.flip_y else -1)
        while words:
            is_word = isinstance(words[-1], str)
            if is_word:
                word_len = self.calc_size(words[-1], scale=scale, font=formatting_data.font)
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
                if token is FormattedTextToken.POP_FORMAT:
                    formatting_data = format_stack.pop()
                if isinstance(token, FormattingData):
                    format_stack.append(formatting_data)
                    formatting_data = formatting_data.copy()
                    formatting_data.update(token)

            if finish_line or not words:
                if formatting_data.align is TextAlign.CENTER:
                    cx = x + (max_line_len - cur_line_len + min_sep) // 2
                else:
                    cx = x
                for word, formatting in line:
                    self.render_string(word, cx, cy, scale=scale, **formatting)
                    cx += self.calc_size(word, scale=scale, font=formatting.font) + min_sep
                line.clear()
                cur_line_len = 0
                cy += vertical_advance
            
    @lru_cache(1024)
    def calc_size(self, text, scale=1, font=None, kerning_enabled=True):
        x = 0
        for char, next_char in itertools.zip_longest(text, text[1:]):
            if kerning_enabled and next_char is not None:
                kerning = self.get_kerning(char, next_char, font_name=font).x
            else:
                kerning = 0
            x += self.get_glyph(char, font_name=font).advance.x + kerning
        return x / 64 * scale / self.pixel_size
    
    @lru_cache(1024)
    def calc_height(self, text, scale=1, full=False, font=None):
        max_y = 0
        min_y = 0
        for char in text:
            glyph = self.get_glyph(char, font_name=font)
            max_y = max(max_y, glyph.bearing.y)
            if full:
                min_y = min(min_y, -glyph.size.y - glyph.bearing.y)
        return abs(max_y - min_y) * scale / self.pixel_size

    def __del__(self):
        if self.vao:
            self.vao.release()
        if self.buffer:
            self.buffer.release()