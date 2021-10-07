from qlibs.gui.window import Window
from qlibs.fonts.font_render import DirectFontRender, FormattedText, FormattingData
from qlibs.math import Matrix4
from qlibs.fonts.font_loader import font_loader
import time

COLORS = {
    "red": (1, 0, 0)
}

win = Window(width=1300, height=1000)

#Load fonts. "default" usually has been assigned a font already, so override has to be set to True in order to replace it
font_loader.get().load_freetype_font("default", "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf", override=True)
font_loader.get().load_freetype_font("mono", "/usr/share/fonts/truetype/freefont/FreeMono.ttf")

rend = DirectFontRender(win.ctx)

#The old way to do formatting wasn't exactly intuitive, so a new one is available
#We can also pass a color_converter callback, which should convert color names(e.g. red) to (r, g, b) tuples
text2 = FormattedText.from_html(
    '''This is normal text <style font=mono> And this one is <style color=#0ff0ff> monospace </style> font </style> 
    more normal text <br> <style color=red font=mono> Another line </style>
    <raw>This counts as a single token and is never split. Like, literally never. Not even max_line_len stops it</raw>
    Can also have special characters and stuff
    <raw><style></style> <>::,,.."la"'</raw>
    ''',
    color_converter=lambda x:COLORS[x]
)

#The old way is still here
text = FormattedText(tokens=[FormattingData(color=(0.9, 0, 0)), "red", FormattingData(color=(0, 0.9, 0)), "green", FormattingData(color=(0, 0, 0.9)), "blue"])

while not win.should_close:
    win.ctx.clear()
    mvp = Matrix4.orthogonal_projection(0, win.size[0], 0, win.size[1])
    rend.render_string(f"Time since epoch - {time.time()}, cache size is {len(rend.cache)}", 30, 20, scale=32, mvp=mvp)
    
    rend.render_multiline(text, 30, 300, 500, scale=32, mvp=mvp)
    rend.render_multiline(text2, 400, 450, 500, scale=32, mvp=mvp)
    
    #Show the effect of kerning
    s = "Ko LT AV"
    rend.render_string(s, 30, 180, scale=32, mvp=mvp)
    rend.render_string(s, 30, 220, scale=32, mvp=mvp, kerning_enabled=False)

    #Rendering at different scales
    y = 400
    for i in range(5, 32*3, 8):
        rend.render_string("Hello, world!", 10, y, scale=i, mvp=mvp)
        y += i + 2

    win.swap()
    win.poll_events()