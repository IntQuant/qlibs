from qlibs.models.compoundmodel import CompoundModel
from qlibs.models.modelrenderer import RenderableModel, Scene

from qlibs.resources import resource_loader, resource_manager

from qlibs.math.matrix import Matrix4
from qlibs.math.vec import Vec

import moderngl_window as mglw

resource_loader.loader.loaders.append(resource_loader.SearchLocationLoader("/home/iquant/programs/MagicaVoxel-0.99.4-alpha-win64/export", "models/"))



class BasicWindowConfig(mglw.WindowConfig):
    gl_version = (3, 3)
    title = "Compound Model"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.scene = Scene()
        self.model = RenderableModel(resource_manager.load_model("models/Stick.obj"), self.scene, self.ctx)
        self.cmp_model = CompoundModel()
        mat = Matrix4.translation_matrix(0, 3, 0) * Matrix4.rotation_euler(0, 0.1, 0)
        self.cmp_model.add_model(self.model)
        self.cmp_model.add_model(self.model, mat, dependency_id=-1)
        self.cmp_model.add_model(self.model, mat, dependency_id=-1)
        self.cmp_model.add_model(self.model, mat, dependency_id=-1)
        self.cmp_model.add_model(self.model, mat, dependency_id=-1)

    def render(self, time, frametime):
        self.ctx.clear(0, 0, 0)
        proj = Matrix4.perspective_projection(45.0, self.window_size[0] / self.window_size[1], 0.1, 1000.0)
        view = Matrix4.look_at(
            Vec(30, 10, 0), Vec(0, 10, 0), Vec(0, 1, 0)
        )
        model = Matrix4.translation_matrix(0, 0, 0)
        self.cmp_model.render(model, view, proj)
        #self.model.render(model, view, proj)


if __name__ == '__main__':
    mglw.run_window_config(BasicWindowConfig)
    
    

