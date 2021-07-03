"""
  Contains drawers of simple shapes.
"""

from array import array

import moderngl

from ..resources.resource_manager import get_storage_of_context
from ..math.matrix import Matrix4, IDENTITY
from ..math import Vec2
from ..util import try_write

from .window import current_context

SHADER_VERTEX = "qlibs/shaders/drawer.vert"
SHADER_FRAGMENT = "qlibs/shaders/drawer.frag"


class ShapeDrawer:
    """
      Special class for drawing simple shapes: lines, triangles and polygons.
      TODO: document parameters
    """
    def __init__(self, ctx=None, prog=None, additional_inputs=tuple()):
        ctx = ctx or current_context.get()
        self.program = prog or get_storage_of_context(ctx).get_program(
            SHADER_VERTEX, SHADER_FRAGMENT
        )
        self.default_z = 0.
        self.ctx = ctx
        self.additional_inputs = additional_inputs
        self.buffer = self.ctx.buffer(reserve=4, dynamic=True)
        self.vao = self.ctx.simple_vertex_array(
            self.program, self.buffer, "in_vert", "color", *self.additional_inputs
        )
        self.prepare()

    def prepare(self):
        self.tr_buffer = array("f")
        self.tr_amount = 0
        self.li_buffer = array("f")
        self.li_amount = 0

    def add_line2d(self, p0: Vec2, p1: Vec2, color=(1, 1, 1), width=1):
        d = p1 - p0
        p = d.perpendicular()
        p.normalize()
        p *= width
        #(x, y), (x+w, y), (x+w, y+h), (x, y+h))
        self.add_polygon((
            (p0.x-p.x, p0.y-p.y),
            (p0.x+p.x, p0.y+p.y),
            (p1.x+p.x, p1.y+p.y),
            (p1.x-p.x, p1.y-p.y),
        ), color=color)

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
        self.li_amount += 1

    def add_line_polygon(self, points, color=(1, 1, 1)):
        for i in range(len(points)):
            self.add_line(points[i-1], points[i], color)
    
    def add_line_rectangle(self, x, y, w, h, color=(1, 1, 1)):
        self.add_line_polygon(((x, y), (x+w, y), (x+w, y+h), (x, y+h)), color)

    def add_line2d_polygon(self, points, **kwargs):
        for i in range(len(points)):
            self.add_line2d(Vec2(*points[i-1]), Vec2(*points[i]), **kwargs)
    
    def add_line2d_rectangle(self, x, y, w, h, **kwargs):
        self.add_line2d_polygon(((x, y), (x+w, y), (x+w, y+h), (x, y+h)), **kwargs)
    
    def add_triangle(self, points, color=(1, 1, 1), additional_data=None):
        assert len(points) == 3
        assert 3 <= len(color) <= 4
        if len(color) == 3:
            color = list(color) + [1]
        
        for i, point in enumerate(points):
            assert 2 <= len(point) <= 3
            if len(point) == 2:
                point = list(point) + [self.default_z]

            self.tr_buffer.extend(map(float, point))
            self.tr_buffer.extend(map(float, color))
            if additional_data is not None:
                self.tr_buffer.extend(additional_data[i])
        self.tr_amount += 1
    
    def add_polygon(self, points, color=(1, 1, 1), additional_data=None):
        for i in range(len(points)-2):
            if additional_data is None:
                self.add_triangle((points[0], points[i+1], points[i+2]), color)
            else:
                self.add_triangle((points[0], points[i+1], points[i+2]), color, (additional_data[0], additional_data[i+1], additional_data[i+2]))
    
    def add_nonconvex_polygon(self, points, center, color=(1, 1, 1)):
        for i in range(len(points)):
            self.add_triangle((center, points[i-1], points[i]), color)
    
    def add_rectangle(self, x, y, w, h, color=(1, 1, 1)):
        self.add_polygon(((x, y), (x+w, y), (x+w, y+h), (x, y+h)), color)
    
    def render(self, mvp=Matrix4(IDENTITY), reset=True, change_context_state=False):
        if change_context_state:
            self.ctx.enable_only(moderngl.NOTHING)
        try_write(self.program, "mvp", mvp.bytes())
        target_len = max(len(self.tr_buffer), len(self.li_buffer))
        armortized_len = 2 ** (target_len.bit_length() + 1)
        min_armortized_len = 2 ** (target_len.bit_length() + 2)
        if self.buffer.size < 4*target_len or self.buffer.size > 4*min_armortized_len:
            self.buffer.orphan(4*armortized_len)            
        self.buffer.write(self.tr_buffer)
        self.vao.render(moderngl.TRIANGLES, vertices=self.tr_amount*3)
        self.buffer.write(self.li_buffer)
        self.vao.render(moderngl.LINES, vertices=self.li_amount*2)
        
        if reset:
            self.prepare()

    def __del__(self):
        self.buffer.release()
        self.vao.release()
