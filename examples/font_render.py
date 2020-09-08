from qlibs.gui.window import Window
from qlibs.fonts.font_render import DirectFontRender
from qlibs.fonts.font_search import find_reasonable_font
from qlibs.math import Matrix4

win = Window()
rend = DirectFontRender(win.ctx, None, font_path=find_reasonable_font())

while not win.should_close:
    win.ctx.clear()
    mvp = Matrix4.orthogonal_projection(0, win.size[0], 0, win.size[1])
    rend.render_multiline("asdf asfdf asd a d da sad df asd fdsfa asadf  fads adsf", 30, 300, 500, scale=32, mvp=mvp)
    win.swap()
    win.poll_events()