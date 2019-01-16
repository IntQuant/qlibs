from vec import Vec
from matrix import Matrix4, IDENTITY
import moderngl
import sdl2
import time
from gui.window_provider import window_provider
import math
from PIL import Image
from array import array


width = 800
height = 600


win = window_provider.Window()

print("Creating context")
ctx = win.ctx
print("Done")
ctx.enable(moderngl.DEPTH_TEST)
query = ctx.query(samples=True, time=True)

prog = ctx.program(
    vertex_shader='''
        #version 330
        
        uniform mat4 mvp;
        
        in vec3 in_vert;
        in vec3 normal;
        
        
        void main() {
            gl_Position = mvp * vec4(in_vert, 1.0);
        }
    ''',
    fragment_shader='''
        #version 330
        
        in vec3 normal;
        out vec3 color;
        
        void main() {
            color = vec3(1, 1, 1);
        }
    ''',
)

import modelloader

Index = modelloader.OBJIndex

obj = modelloader.OBJLoader()
obj.load_path("C:/Users/IQuant/Desktop/test3.obj")

res = obj.resolve(Index.VX, Index.VY, Index.VZ)

vbo = ctx.buffer(res.tobytes())

vao = ctx.simple_vertex_array(prog, vbo, 'in_vert')

running = True

while running:
    ctx.clear(0, 0, 0)

    proj = Matrix4.perspective_projection(45.0, width / height, 0.1, 1000.0)
    
    #r = math.radians((time.time()* 10))
    r = 0
    d = 10

    view = Matrix4.look_at(Vec(math.cos(r) * d, 10, math.sin(r) * d), Vec(0, 0, 0), Vec(0, 1, 0))
    
    model = Matrix4(IDENTITY)

    mvp = proj * view * model
    
    prog['mvp'].write(mvp.bytes())
    with query:
        vao.render(moderngl.TRIANGLES)
    
    print(query.samples)


    for event in win.get_events():
        if event.type == sdl2.SDL_QUIT:
            running = False
        #print(event.type)
    sdl2.SDL_GL_SwapWindow(win.window)
    sdl2.SDL_Delay(10)
#Image.frombytes('RGB', fbo.size, fbo.read(), 'raw', 'RGB', 0, -1).show()
