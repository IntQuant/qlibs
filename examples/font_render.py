from qlibs.gui.window import Window
from qlibs.fonts.font_render import DirectFontRender, FormattedText, FormattingData
from qlibs.math import Matrix4
from qlibs.fonts.font_loader import font_loader
import time

win = Window(width=1300)

font_loader.get().load_freetype_font("default", "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf", override=True)
font_loader.get().load_freetype_font("mono", "/usr/share/fonts/truetype/freefont/FreeMono.ttf")
rend = DirectFontRender(win.ctx)
text = FormattedText(tokens=[FormattingData(color=(0.9, 0, 0)), "red", FormattingData(color=(0, 0.9, 0)), "green", FormattingData(color=(0, 0, 0.9)), "blue"])
text2 = FormattedText(tokens=["This",  "is", "normal", "text", FormattingData(font="mono"), "And", "this", "one", "is", "monospace", "s", "t"])
while not win.should_close:
    win.ctx.clear()
    mvp = Matrix4.orthogonal_projection(0, win.size[0], 0, win.size[1])
    rend.render_string(f"lalala {time.time()}", 30, 400, scale=32, mvp=mvp)
    
    #Might want to fix this one being a bit blurry
    s = "Ko LT AV"
    rend.render_string(s, 30, 200, scale=32*3, mvp=mvp)
    rend.render_string(s, 30, 300, scale=32*3, mvp=mvp, kerning_enabled=False)
    rend.render_multiline(text, 30, 500, 500, scale=32, mvp=mvp)
    rend.render_multiline(text2, 30, 100, 300, scale=32, mvp=mvp)

    win.swap()
    win.poll_events()