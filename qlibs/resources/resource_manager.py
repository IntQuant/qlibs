import moderngl
from .resource_loader import get_res_texture, get_res_data, get_res_path, get_image_data
from ..models.modelloader import OBJLoader

pcs_storage = dict()
modelloader = OBJLoader()

def get_storage_of_context(ctx):
    i = id(ctx)
    storage = pcs_storage.get(i)
    if storage is None:
        storage = PerContextStorage(ctx)
        pcs_storage[i] = storage
    return storage


def load_model(name):
    modelloader.load_path(get_res_path(name))
    return modelloader.get_obj()

class PerContextStorage:
    """Storage for context-specific things"""
    def __init__(self, ctx):
        self.ctx = ctx
        self.program_storage = dict()
        self.texture_storage = dict()

    def get_program(
        self, vertex_shader_name, fragment_shader_name, geometry_shader_name=None
    ):
        identifier = (vertex_shader_name, fragment_shader_name, geometry_shader_name)
        if identifier in self.program_storage:
            return self.program_storage[identifier]

        vsource = get_res_data(vertex_shader_name)
        fsource = get_res_data(fragment_shader_name)
        gsource = (
            get_res_data(geometry_shader_name)
            if geometry_shader_name is not None
            else None
        )
        prog = self.ctx.program(
            vertex_shader=vsource, fragment_shader=fsource, geometry_shader=gsource
        )
        self.program_storage[identifier] = prog
        return prog

    def get_texture(self, r_path, srgb=False):
        key = (r_path, srgb)
        texture = self.texture_storage.get(key, None)
        if texture is None:
            img = get_image_data(r_path)
            if srgb:
                texture = self.ctx.texture(img.size, 4, img.data, internal_format=0x8C41)
            else:
                texture = self.ctx.texture(img.size, 4, img.data)
            texture.build_mipmaps()
            self.texture_storage[key] = texture
        return texture
