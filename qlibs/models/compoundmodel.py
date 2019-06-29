from ..math import Matrix4, IDENTITY

class CompoundModel:
    def __init__(self):
        self.submodels = []
        self.reference = []
        self.matrices = []
    
    def add_model(self, model, matrix=None, dependency_id=None):
        self.submodels.append(model)
        self.reference.append(dependency_id)
        self.matrices.append(matrix or Matrix4(IDENTITY))
    
    def render(self, m, v, p):
        ms = []
        for model, ref, matrix in zip(self.submodels, self.reference, self.matrices):
            if ref is None:
                ms.append(m * matrix)
            else:
                ms.append(ms[ref] * matrix)
            model.render(ms[-1], v, p)


    