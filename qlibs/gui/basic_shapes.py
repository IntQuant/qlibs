from array import array

import moderngl

from ..resources.resource_manager import get_storage_of_context
from ..math.matrix import Matrix4, IDENTITY
from ..util import try_write

SHADER_VERTEX = "qlibs/shaders/drawer.vert"
SHADER_FRAGMENT = "qlibs/shaders/drawer.frag"


class ShapeDrawer:
    def __init__(self, ctx, prog=None):
        self.program = prog or get_storage_of_context(ctx).get_program(
            SHADER_VERTEX, SHADER_FRAGMENT
        )
        self.default_z = 0.
        self.ctx= ctx
        self.buffer = None
        self.prepare()

    def prepare(self):
        self.tr_buffer = array("f")
        self.li_buffer = array("f")

    def add_line(self, p0, p1, color=(1, 1, 1)):
        if len(color) == 3:
            color = list(color) + [1]
        if len(p0) == 2:
            p0 = list(p0) + [self.default_z]
        if len(p1) == 2:
            p1 = list(p1) + [self.default_z]
        assert len(color) == 4
        assert len(p0) == 3
        assert len(p1) == 3
        self.li_buffer.extend(map(float, p0))
        self.li_buffer.extend(map(float, color))
        self.li_buffer.extend(map(float, p1))
        self.li_buffer.extend(map(float, color))

    def add_triangle(self, points, color=(1, 1, 1)):
        assert len(points) == 3
        assert 3 <= len(color) <= 4
        if len(color) == 3:
            color = list(color) + [1]

        for point in points:
            assert 2 <= len(point) <= 3
            if len(point) == 2:
                point = list(point) + [self.default_z]

            self.tr_buffer.extend(map(float, point))
            self.tr_buffer.extend(map(float, color))
    
    def add_polygon(self, points, color=(1, 1, 1)):
        for i in range(len(points)-2):
            self.add_triangle((points[0], points[i+1], points[i+2]), color)
    
    def add_rectangle(self, x, y, w, h, color=(1, 1, 1)):
        self.add_polygon(((x, y), (x+w, y), (x+w, y+h), (x, y+h)), color)
    
    def render(self, mvp=Matrix4(IDENTITY), reset=True, change_context_state=True):
        if change_context_state:
            self.ctx.enable_only(moderngl.NOTHING)
        try_write(self.program, "mvp", mvp.bytes())
        target_len = max(len(self.tr_buffer), len(self.li_buffer))
        amortized_len = 2 ** (target_len.bit_length() + 1)
        min_amortized_len = 2 ** (target_len.bit_length() + 2)
        if (self.buffer is None 
            or self.buffer.size < 4*target_len 
            or self.buffer.size > 4*min_amortized_len
            ):
            self.buffer = self.ctx.buffer(reserve=4*amortized_len, dynamic=True)
            self.vao = self.ctx.simple_vertex_array(
                self.program, self.buffer, "in_vert", "color"
            )
        self.buffer.write(self.tr_buffer)
        self.vao.render(moderngl.TRIANGLES, vertices=len(self.tr_buffer))
        self.buffer.write(self.li_buffer)
        self.vao.render(moderngl.LINES, vertices=len(self.li_buffer))
        
        if reset:
            self.prepare()
