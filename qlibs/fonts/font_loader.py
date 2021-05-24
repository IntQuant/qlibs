import warnings
import freetype
from .font_search import find_reasonable_font
from contextvars import ContextVar
from collections import defaultdict

class GlyphProvider:
    def __init__(self):
        pass

    def get(self, char, size=48):
        raise NotImplemented()


class FreetypeGlyphProvider(GlyphProvider):
    def __init__(self, file):
        self.font = freetype.Face(file)

    def get(self, char, size=48):
        self.font.set_pixel_sizes(0, size)
        self.font.load_char(char)
        return self.font.glyph


class FontLoader:
    def __init__(self):
        self.mapping = defaultdict(list)
        reasonable_font = find_reasonable_font()
        if reasonable_font is None:
            warnings.warn(RuntimeWarning("No default font found! (Could not find system font)"))
        else:
            self.mapping["default"].append(FreetypeGlyphProvider(reasonable_font))
    
    def get(self, font_name, char):
        for provider in self.mapping[font_name]:
            v = provider.get(char)
            if v is not None:
                return v
        raise RuntimeError(f"Character '{char}' in font '{font_name}' not found")


font_loader: ContextVar[FontLoader] = ContextVar("font_loader", default=FontLoader())