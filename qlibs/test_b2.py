from vec import Vec
from matrix import Matrix4, IDENTITY
from util import try_write
import modelloader
from gui.window_provider import window_provider

import moderngl
import sdl2

import time
import math
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
        uniform mat4 m;
        uniform mat4 v;
        uniform mat4 p;
        uniform vec3 light_pos;
        
        in vec3 in_vert;
        in vec3 normal;
        out vec3 normal_cam;
        out vec3 light_dir_cam;
        out float distance;
        
        void main() {
            gl_Position = mvp * vec4(in_vert, 1.0);
            vec3 vert_cam = (v * m * vec4(in_vert, 1.0)).xyz;
            vec3 eye_dir = vec3(0, 0, 0) - vert_cam;
            light_dir_cam = light_pos + eye_dir;
            normal_cam = (v * m * vec4(normal, 1)).xyz;
            distance = length(eye_dir) + length(light_dir_cam);
        }
    ''',
    fragment_shader='''
        #version 330
        
        in vec3 normal_cam;
        in vec3 light_dir_cam;
        in float distance;
        out vec3 color;
        
        void main() {
            vec3 n = normalize(normal_cam);
            vec3 l = normalize(light_dir_cam);
            
            color = (vec3(1, 1, 1) * clamp(dot(n, l), 0, 1) * 60 / (distance * distance)) + vec3(0.1, 0.1, 0.1); 
        }
    ''',
)



Index = modelloader.OBJIndex

obj = modelloader.OBJLoader()
obj.load_path("C:/Users/IQuant/Desktop/test3.obj")

res = obj.resolve(Index.VX, Index.VNX, Index.VY, Index.VNY, Index.VZ, Index.VNZ)

vbo = ctx.buffer(res.tobytes())

vao = ctx.simple_vertex_array(prog, vbo, 'in_vert', "normal")

running = True

lamp_loc = Vec(0, 0, 0) #TODO

while running:
    ctx.clear(0, 0, 0)

    proj = Matrix4.perspective_projection(45.0, width / height, 0.1, 1000.0)
    
    r = math.radians((time.time()* 10))
    #r = 0
    d = 10
    
    view = Matrix4.look_at(Vec(math.cos(r) * d, 10, math.sin(r) * d), Vec(0, 0, 0), Vec(0, 1, 0))
    
    model = Matrix4(IDENTITY)
    
    mvp = proj * view * model
    
    try_write(prog, 'mvp', mvp.bytes())
    try_write(prog, 'm', model.bytes())
    try_write(prog, 'v', view.bytes())
    try_write(prog, 'p', proj.bytes())
    
    lamp_loc_cam = (view * lamp_loc).as_n_d(3)
    print(lamp_loc_cam)
    #lamp_loc_cam = Vec(0, 0, 0)
    try_write(prog, 'light_pos', lamp_loc_cam.bytes())

    #with query:
    vao.render(moderngl.TRIANGLES)
    
    #print('It took %d nanoseconds' % query.elapsed)
    #print('to render %d samples' % query.samples)
    #print(query.samples)


    for event in win.get_events():
        if event.type == sdl2.SDL_QUIT:
            running = False
        #print(event.type)
    sdl2.SDL_GL_SwapWindow(win.window)
    sdl2.SDL_Delay(10)
#Image.frombytes('RGB', fbo.size, fbo.read(), 'raw', 'RGB', 0, -1).show()
