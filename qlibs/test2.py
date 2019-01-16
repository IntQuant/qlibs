from pyrr import Matrix44
from vec import Vec
from matrix import Matrix4
import numpy as np

pvec = np.array((10, 0, 0, 1))
pmat = Matrix44.look_at([10, 10, 5], [0, 0, 0], [0, 0, 1])
print(np.dot(pmat, pvec))
qvec = Vec(10, 0, 0, 1)
qmat = Matrix4.look_at(Vec(10, 10, 5), Vec(0, 0, 0), Vec(0, 0, 1))
print(qmat * qvec)

