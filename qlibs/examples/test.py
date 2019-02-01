import moderngl
import sdl2
from PIL import Image

import time
import math
from array import array

from vec import Vec
from matrix import Matrix4, IDENTITY
from gui.window_provider import window_provider
from util import try_write
import modelloader
import resource_loader

width = 800
height = 600


win = window_provider.Window()

print("Creating context")
ctx = win.ctx
print("Done")
ctx.enable(moderngl.DEPTH_TEST)
query = ctx.query(samples=True, time=True)

prog = ctx.program(
    vertex_shader=resource_loader.get_res_data("shaders/basic_textures_shader.glsh"),
    fragment_shader=resource_loader.get_res_data("shaders/basic_textures_fragment_shader.glsh"),
)

Index = modelloader.OBJIndex

obj = modelloader.OBJLoader()
obj.load_path("C:/Users/IQuant/Desktop/test2.obj")

res = obj.resolve(Index.VX, Index.VNX, Index.VTX, Index.VY, Index.VNY, Index.VTY, Index.VZ, Index.VNZ, Index.VTZ)

vbo = ctx.buffer(res.tobytes())

vao = ctx.simple_vertex_array(prog, vbo, 'in_vert', "normal", "uv")

running = True

lamp_loc = Vec(0, 20, 0) #TODO

img = Image.open('C:/Users/IQuant/Desktop/miner_spatial_x2.png').transpose(Image.FLIP_TOP_BOTTOM).convert('RGB')
texture = ctx.texture(img.size, 3, img.tobytes())
texture.build_mipmaps()

while running:
    ctx.clear(0, 0, 0)
    
    texture.use()
    
    proj = Matrix4.perspective_projection(45.0, width / height, 0.1, 1000.0)
    
    r = math.radians((time.time() * 10))
    #r = 0
    d = 50
    
    view = Matrix4.look_at(Vec(math.cos(r) * d, 10, math.sin(r) * d), Vec(0, 0, 0), Vec(0, 1, 0))
    
    model = Matrix4.translation_matrix(0, 0, 0)
    
    mvp = proj * view * model
    
    try_write(prog, 'mvp', mvp.bytes())
    try_write(prog, 'm', model.bytes())
    try_write(prog, 'v', view.bytes())
    try_write(prog, 'p', proj.bytes())
    
    
    try_write(prog, 'light', lamp_loc.bytes())

    
    vao.render(moderngl.TRIANGLES)
    


    for event in win.get_events():
        if event.type == sdl2.SDL_QUIT:
            running = False
        #print(event.type)
    sdl2.SDL_GL_SwapWindow(win.window)
    sdl2.SDL_Delay(10)
#Image.frombytes('RGB', fbo.size, fbo.read(), 'raw', 'RGB', 0, -1).show()
