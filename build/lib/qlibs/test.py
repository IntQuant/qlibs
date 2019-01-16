from vec import Vec
from matrix import Matrix4, IDENTITY

#vec = Vec(0, 0, 0, 1)
width = 800
height = 600


proj = Matrix4.perspective_projection(45.0, width / height, 0.1, 100.0)

view = Matrix4.look_at(Vec(3, 3, -4), Vec(0, 0, 0), Vec(0, 1, 0))

model = Matrix4(IDENTITY)

#print(proj)
#print(view)
#print(model)

mvp = proj * view * model#proj * view * model

import moderngl

ctx = moderngl.create_standalone_context(330)
ctx.enable(moderngl.DEPTH_TEST)

prog = ctx.program(
    vertex_shader='''
        #version 330
        
        uniform mat4 mvp;
        
        in vec3 in_vert;
        in vec3 in_color;
        out vec3 v_color;
        
        void main() {
            v_color = in_color;
            gl_Position = mvp * vec4(in_vert, 1.0);
        }
    ''',
    fragment_shader='''
        #version 330
        
        in vec3 v_color;
        out vec3 color;

        void main() {
            color = v_color;
        }
    ''',
)

from PIL import Image
from array import array

triangles = array("f", 
  [-1,-1,-1,
    -1,-1, 1,
    -1, 1, 1,
    1, 1,-1,
    -1,-1,-1,
    -1, 1,-1,
    1,-1, 1,
    -1,-1,-1,
    1,-1,-1,
    1, 1,-1,
    1,-1,-1,
    -1,-1,-1,
    -1,-1,-1,
    -1, 1, 1,
    -1, 1,-1,
    1,-1, 1,
    -1,-1, 1,
    -1,-1,-1,
    -1, 1, 1,
    -1,-1, 1,
    1,-1, 1,
    1, 1, 1,
    1,-1,-1,
    1, 1,-1,
    1,-1,-1,
    1, 1, 1,
    1,-1, 1,
    1, 1, 1,
    1, 1,-1,
    -1, 1,-1,
    1, 1, 1,
    -1, 1,-1,
    -1, 1, 1,
    1, 1, 1,
    -1, 1, 1,
    1,-1, 1])
colors = array('f', [
    0.583,  0.771,  0.014,
    0.609,  0.115,  0.436,
    0.327,  0.483,  0.844,
    0.822,  0.569,  0.201,
    0.435,  0.602,  0.223,
    0.310,  0.747,  0.185,
    0.597,  0.770,  0.761,
    0.559,  0.436,  0.730,
    0.359,  0.583,  0.152,
    0.483,  0.596,  0.789,
    0.559,  0.861,  0.639,
    0.195,  0.548,  0.859,
    0.014,  0.184,  0.576,
    0.771,  0.328,  0.970,
    0.406,  0.615,  0.116,
    0.676,  0.977,  0.133,
    0.971,  0.572,  0.833,
    0.140,  0.616,  0.489,
    0.997,  0.513,  0.064,
    0.945,  0.719,  0.592,
    0.543,  0.021,  0.978,
    0.279,  0.317,  0.505,
    0.167,  0.620,  0.077,
    0.347,  0.857,  0.137,
    0.055,  0.953,  0.042,
    0.714,  0.505,  0.345,
    0.783,  0.290,  0.734,
    0.722,  0.645,  0.174,
    0.302,  0.455,  0.848,
    0.225,  0.587,  0.040,
    0.517,  0.713,  0.338,
    0.053,  0.959,  0.120,
    0.393,  0.621,  0.362,
    0.673,  0.211,  0.457,
    0.820,  0.883,  0.371,
    0.982,  0.099,  0.879
])

x, y, z = triangles[0::3], triangles[1::3], triangles[2::3]
r, g, b = colors[0::3], colors[1::3], colors[2::3]

res = array('f')

for e in zip(x, y, z, r, g, b):
    #print(e)
    res.extend(e)

#print(res)

prog['mvp'].write(mvp.bytes_dtype())



vbo = ctx.buffer(res.tobytes())
#vbo = ctx.buffer(triangles.tobytes() + colors.tobytes())
vao = ctx.simple_vertex_array(prog, vbo, 'in_vert', 'in_color')

fbo = ctx.simple_framebuffer((width, height))
fbo.use()
fbo.clear(0.0, 0.0, 0.0, 1.0)

vao.render(moderngl.TRIANGLES)

Image.frombytes('RGB', fbo.size, fbo.read(), 'raw', 'RGB', 0, -1).show()
