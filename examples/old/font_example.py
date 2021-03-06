"""
  Note: requires moderngl_window
"""

from qlibs.fonts.font_search import find_reasonable_font
from qlibs.fonts.font_render import DirectFontRender
from qlibs.math.matrix import Matrix4
from qlibs.math.vec import IVec
import freetype
import moderngl_window as mglw

font_path = find_reasonable_font()

print("Loading", font_path)
font = freetype.Face(font_path)
font.set_pixel_sizes(0, 48)
print(f"Font family {font.family_name}")
print(f"Char amount {len(list(font.get_chars()))}")
print(f"Font size {font.size.height}")

class Exit(Exception): pass


class BasicWindowConfig(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "Text rendering"
    vsync = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.renderer = DirectFontRender(self.ctx, font)

    def render(self, time, frametime):
        ortho = Matrix4.orthogonal_projection(0, self.window_size[0], 0, self.window_size[1])
        
        self.renderer.render_string("%.2f" % time, 100, 100, 1, mvp=ortho)
        self.renderer.render_string("Приветик!", 100, 200, 1, mvp=ortho)

        if time > 30:
            raise Exit()
        


if __name__ == '__main__':
    try:
        mglw.run_window_config(BasicWindowConfig)
    except Exit:
        pass
