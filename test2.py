import numpy as np

from pyrr import Matrix44
from matrix import Matrix4

mat = [[0, 10, 0, 0],
       [0, 2, 1, 2],
       [1, 3, 5, 3],
       [4, 3, 2, 1]
]

nmat = np.array(mat)
mmat = Matrix4(nmat.flatten)
print(nmat)
print(mmat)
