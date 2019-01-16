from vec import Vec
from matrix import Matrix4, IDENTITY
import moderngl
import sdl2
import time
from gui.window_provider import window_provider
import math
from PIL import Image
from array import array
from util import try_write

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
        
        uniform mat4 m;
        
        in vec3 in_vert;
        in vec3 normal;
        in vec2 uv;
        
        out vec3 v_vert;
        out vec2 v_uv;
        out vec3 f_normal;
        
        
        
        
        void main() {
            
            vec4 t_vert = mvp * vec4(in_vert, 1.0);
            gl_Position = t_vert;
            v_vert = (m * vec4(in_vert, 1.0)).xyz;
            f_normal = (m * vec4(normal, 0)).xyz;
            
            v_uv = uv;
        }
    ''',
    fragment_shader='''
        #version 330

        uniform sampler2D text;
        
        in vec3 f_normal;
        in vec2 v_uv;
        
        uniform vec3 light;
        
        in vec3 v_vert;
        out vec3 color;
        
        void main() {
            
            vec3 ld = light-v_vert;
            
            float distance_sq = ld.x * ld.x + ld.y * ld.y + ld.z * ld.z;
            
            float lum = (clamp(dot(normalize(light - v_vert), normalize(f_normal)), 0.0, 1.0) * 200 / (distance_sq))* 0.9 + 0.1;
            
            color = texture(text, v_uv).xyz  * lum;
        }
    ''',
)

import modelloader

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
