"""
import numpy as np

from pyrr import Matrix44
from matrix import Matrix4

mat0 = [[0, 10, 0, 0],
       [0, 2, 1, 2],
       [1, 3, 5, 3],
       [4, 3, 2, 1]
       ]
mat1 = [[0, 10, 0, 0],
       [0, 56, 1, 2],
       [1, 3, 3, 3],
       [4, 3, 2, 1]
       ]


nmat0 = np.array(mat0)
fmat0 = Matrix44(nmat0)
mmat0 = Matrix4(nmat0.flatten())

nmat1 = np.array(mat1)
fmat1 = Matrix44(nmat1)
mmat1 = Matrix4(nmat1.flatten())

#print(nmat0)
print(fmat0)
print(mmat0)

#print(nmat1)
print(fmat1)
print(mmat1)

print(fmat0 * fmat1)
print(mmat0 * mmat1)
"""

import moderngl
import numpy as np

from PIL import Image

ctx = moderngl.create_standalone_context()

prog = ctx.program(
    vertex_shader='''
        #version 330

        in vec2 in_vert;
        in vec3 in_color;

        out vec3 v_color;

        void main() {
            v_color = in_color;
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }
    ''',
    fragment_shader='''
        #version 330

        in vec3 v_color;

        out vec3 f_color;

        void main() {
            f_color = v_color;
        }
    ''',
)

x = np.linspace(-1.0, 1.0, 50)
y = np.random.rand(50) - 0.5
r = np.ones(50)
g = np.zeros(50)
b = np.zeros(50)

vertices = np.dstack([x, y, r, g, b])

print(x, y, r, g, b)
print("="*20)
print(vertices)
