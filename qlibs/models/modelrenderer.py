import moderngl

from . import modelloader
from ..resources.resource_loader import get_res_texture, get_res_data
from ..resources.resource_manager import get_storage_of_context
from ..util import try_write
from ..math.vec import Vec


def make_texture_program(ctx):
    storage = get_storage_of_context(ctx)
    return storage.get_program(
        vertex_shader_name="qlibs/shaders/modelrender.vert",
        fragment_shader_name="qlibs/shaders/lighting.frag",
    )


class MaterialData:
    def __init__(self, material, vbo, vao):
        self.material = material
        self.vbo = vbo
        self.vao = vao


class Scene:
    def __init__(self):
        self.light_direction = Vec(0.1, 1, 1)
        self.light_direction.normalize()
        self.light_color = Vec(1, 1, 0.6)

    def __setattr__(self, key, value):
        if key == "light_direction":
            value = Vec(value)
            value.normalize()
        super().__setattr__(key, value)


class RenderableModel:
    """
      Model wrapper which can render models
    """
    def __init__(self, model, scene, ctx, program=None):
        self.model = model
        self.ctx = ctx
        self.scene = scene
        self.texture_program = program
        self.reset()
        self.prepare()

    def reset(self):
        self.ready = False
        self.hooked_textures = dict()
        self.textured_data = dict()
        self.plain_data = dict()

    def prepare(self):
        program = self.texture_program or make_texture_program(self.ctx)

        if self.ready:
            return
        self.ready = True

        for mat, data in self.model.iter_materials_textured(
            *modelloader.FORMAT_TEXTURES
        ):
            if len(data) == 0:
                continue
            if mat.mat_name not in self.model.materials:
                print(f"Could not find material {mat.mat_name}, skipping")
                continue
            
            mat = self.model.materials[mat.mat_name]
            mat.process()
            vbo = self.ctx.buffer(data)
            vao = self.ctx.simple_vertex_array(program, vbo, "in_vert", "normal", "uv")
            md = MaterialData(mat, vbo, vao)
            self.textured_data[mat.name] = md

            storage = get_storage_of_context(self.ctx)

            for p in modelloader.MATERIAL_LIGHT_PROPERTIES_MAP:
                name = mat.prc_params[p]
                if name is not None:
                    self.hooked_textures[name] = storage.get_texture(name)

    def render(self, m, v, p, mvp=None):
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)
        prog = self.texture_program or make_texture_program(self.ctx)

        if mvp is None:
            mvp = p * v * m

        try_write(prog, "mvp", mvp.bytes())
        try_write(prog, "m", m.bytes())
        try_write(prog, "v", v.bytes())
        try_write(prog, "p", p.bytes())

        try_write(prog, "light_dir", self.scene.light_direction.bytes())
        try_write(prog, "light_col", self.scene.light_color.bytes())

        for name, matdata in self.textured_data.items():
            mat, vao = matdata.material, matdata.vao
            self.hooked_textures[mat.prc_params["map_Kd"]].use()
            vao.render(moderngl.TRIANGLES)
