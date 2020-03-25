"""
  Requires model to be available (none are bundled with qlibs)
"""

from qlibs.resources import resource_loader, resource_manager
from qlibs.math.vec import MVec

resource_loader.loader.loaders.append(resource_loader.SearchLocationLoader("/home/iquant/programs/MagicaVoxel-0.99.4-alpha-win64/export", "models/"))

model = resource_manager.load_model("models/Stick.obj")

min_vec = MVec(model.v[0])
max_vec = MVec(model.v[0])

for v in model.v:
    x, y, z = v
    
    if x > max_vec.x:
        max_vec.x = x
    if y > max_vec.y:
        max_vec.y = y
    if z > max_vec.z:
        max_vec.z = z
    
    if x < min_vec.x:
        min_vec.x = x
    if y < min_vec.y:
        min_vec.y = y
    if z < min_vec.z:
        min_vec.z = z
        
print(min_vec)
print(max_vec)
print(max_vec - min_vec)

