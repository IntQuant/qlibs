import warnings
import freetype

from qlibs.resources.resource_loader import get_res_path
from qlibs.math import Vec2
from .font_search import find_reasonable_font
from contextvars import ContextVar
from collections import defaultdict

class GlyphProvider:
    def __init__(self):
        pass

    def get(self, char, size=48):
        raise NotImplemented()
    
    def get_font_kerning(self, left_char, right_char, size=48):
        return None
    
    @property
    def priority(self):
        return 0


class FreetypeGlyphProvider(GlyphProvider):
    def __init__(self, file, priority=0):
        self.font = freetype.Face(file)
        self._priority = priority

    def get(self, char, size=48):
        self.font.set_pixel_sizes(0, size)
        self.font.load_char(char)
        return self.font.glyph
    
    def get_font_kerning(self, left_char, right_char, size=48):
        self.font.set_pixel_sizes(0, size)
        vec = self.font.get_kerning(left_char, right_char)
        return Vec2(vec.x, vec.y)
    
    @property
    def priority(self):
        return self._priority


class FontLoader:
    def __init__(self):
        self._mapping = defaultdict(list)
        reasonable_font = find_reasonable_font()
        if reasonable_font is None:
            warnings.warn(RuntimeWarning("No default font found! (Could not find system font)"))
        else:
            self.load_freetype_font("default", reasonable_font, priority=-1)
    
    def load_freetype_font(self, font_name, path, override=False, priority=0):
        path = get_res_path(path)
        if override:
            self._mapping[font_name].clear()
        self._mapping[font_name].append(FreetypeGlyphProvider(path, priority=priority))
        self._mapping[font_name].sort(reverse=True, key=lambda x:x.priority)
    
    def get(self, font_name, char, pixel_size=48):
        for provider in self._mapping[font_name]:
            v = provider.get(char, size=pixel_size)
            if v is not None:
                return v
        raise RuntimeError(f"Character '{char}' in font '{font_name}' not found")
    
    def get_kerning(self, font_name, left_char, right_char, pixel_size=48):
        for provider in self._mapping[font_name]:
            v = provider.get_font_kerning(left_char, right_char, size=pixel_size)
            if v is not None:
                return v
        return Vec2(0, 0)


font_loader: ContextVar[FontLoader] = ContextVar("font_loader", default=FontLoader())