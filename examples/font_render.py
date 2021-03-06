from qlibs.gui.window import Window
from qlibs.fonts.font_render import DirectFontRender, FormattedText, FormattingData
from qlibs.math import Matrix4
import time

win = Window()
rend = DirectFontRender(win.ctx)
text = FormattedText(tokens=[FormattingData(color=(0.9, 0, 0)), "red", FormattingData(color=(0, 0.9, 0)), "green", FormattingData(color=(0, 0, 0.9)), "blue"])
while not win.should_close:
    win.ctx.clear()
    mvp = Matrix4.orthogonal_projection(0, win.size[0], 0, win.size[1])
    #rend.render_multiline("asdf asfdf asd a d da sad df asd fdsfa asadf  fads adsf", 30, 300, 500, scale=32, mvp=mvp)
    rend.render_string(f"lalala {time.time()}", 30, 400, scale=32, mvp=mvp)
    rend.render_multiline(text, 30, 300, 500, scale=32, mvp=mvp)
    win.swap()
    win.poll_events()