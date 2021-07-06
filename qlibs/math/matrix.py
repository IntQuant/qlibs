"""
  Matrix module
"""

from array import array
import math
import sys

from .vec import IVec, MVec as Vec

ZEROS_16 = [0] * 16
IDENTITY = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]

__all__ = ["Matrix4"]

def _gauss_jordan(m, eps = 1.0/(10**10)):
  """Puts given matrix (2D array) into the Reduced Row Echelon Form.
     Returns True if successful, False if 'm' is singular.
     NOTE: make sure all the matrix items support fractions! Int matrix will NOT work!
     Written by Jarno Elonen in April 2005, released into Public Domain"""
  (h, w) = (len(m), len(m[0]))
  for y in range(0,h):
    maxrow = y
    for y2 in range(y+1, h):    # Find max pivot
      if abs(m[y2][y]) > abs(m[maxrow][y]):
        maxrow = y2
    (m[y], m[maxrow]) = (m[maxrow], m[y])
    if abs(m[y][y]) <= eps:     # Singular?
      return False
    for y2 in range(y+1, h):    # Eliminate column y
      c = m[y2][y] / m[y][y]
      for x in range(y, w):
        m[y2][x] -= m[y][x] * c
  for y in range(h-1, 0-1, -1): # Backsubstitute
    c  = m[y][y]
    for y2 in range(0,y):
      for x in range(w-1, y-1, -1):
        m[y2][x] -=  m[y][x] * m[y2][y] / c
    m[y][y] /= c
    for x in range(h, w):       # Normalize row y
      m[y][x] /= c
  return True


def _inv(M):
  """
  return the inv of the matrix M
  """
  #clone the matrix and append the identity matrix
  # [int(i==j) for j in range_M] is nothing but the i(th row of the identity matrix
  m2 = [row[:]+[int(i==j) for j in range(len(M) )] for i,row in enumerate(M) ]
  # extract the appended matrix (kind of m2[m:,...]
  return [row[len(M[0]):] for row in m2] if _gauss_jordan(m2) else None

class _PyMatrix4Base:
    __slots__ = ("_data",)

    def __init__(self, data=None):
        """
        Initialize matrix with 16 elements array (*data*) of *dtype* type
        """
        if data is not None:
            self._data = array('f', data)
        else:
            self._data = array('f', ZEROS_16)
    
    def __getitem__(self, key):
        x, y = key
        assert 0 <= x < 4 and 0 <= y < 4
        return self._data[x * 4 + y]

    def __setitem__(self, key, value):
        x, y = key
        assert 0 <= x < 4 and 0 <= y < 4
        self._data[x * 4 + y] = value

    def __eq__(self, other):
        return self._data == other._data

    def bytes(self, dtype="f"):
        """
        Converts internal array to bytes
        """
        return self._data.tobytes()

    def __repr__(self):
        if list(self._data) == IDENTITY:
            return "Matrix4(IDENTITY)"
        if list(self._data) == ZEROS_16:
            return "Matrix4(ZEROS_16)"
        return f"Matrix4({list(self._data)})"

    def __matmul__(self, other):
        res = self.__class__()

        res._data[0] = (
            other._data[0] * self._data[0]
            + other._data[1] * self._data[4]
            + other._data[2] * self._data[8]
            + other._data[3] * self._data[12]
        )
        res._data[1] = (
            other._data[0] * self._data[1]
            + other._data[1] * self._data[5]
            + other._data[2] * self._data[9]
            + other._data[3] * self._data[13]
        )
        res._data[2] = (
            other._data[0] * self._data[2]
            + other._data[1] * self._data[6]
            + other._data[2] * self._data[10]
            + other._data[3] * self._data[14]
        )
        res._data[3] = (
            other._data[0] * self._data[3]
            + other._data[1] * self._data[7]
            + other._data[2] * self._data[11]
            + other._data[3] * self._data[15]
        )
        res._data[4] = (
            other._data[4] * self._data[0]
            + other._data[5] * self._data[4]
            + other._data[6] * self._data[8]
            + other._data[7] * self._data[12]
        )
        res._data[5] = (
            other._data[4] * self._data[1]
            + other._data[5] * self._data[5]
            + other._data[6] * self._data[9]
            + other._data[7] * self._data[13]
        )
        res._data[6] = (
            other._data[4] * self._data[2]
            + other._data[5] * self._data[6]
            + other._data[6] * self._data[10]
            + other._data[7] * self._data[14]
        )
        res._data[7] = (
            other._data[4] * self._data[3]
            + other._data[5] * self._data[7]
            + other._data[6] * self._data[11]
            + other._data[7] * self._data[15]
        )
        res._data[8] = (
            other._data[8] * self._data[0]
            + other._data[9] * self._data[4]
            + other._data[10] * self._data[8]
            + other._data[11] * self._data[12]
        )
        res._data[9] = (
            other._data[8] * self._data[1]
            + other._data[9] * self._data[5]
            + other._data[10] * self._data[9]
            + other._data[11] * self._data[13]
        )
        res._data[10] = (
            other._data[8] * self._data[2]
            + other._data[9] * self._data[6]
            + other._data[10] * self._data[10]
            + other._data[11] * self._data[14]
        )
        res._data[11] = (
            other._data[8] * self._data[3]
            + other._data[9] * self._data[7]
            + other._data[10] * self._data[11]
            + other._data[11] * self._data[15]
        )
        res._data[12] = (
            other._data[12] * self._data[0]
            + other._data[13] * self._data[4]
            + other._data[14] * self._data[8]
            + other._data[15] * self._data[12]
        )
        res._data[13] = (
            other._data[12] * self._data[1]
            + other._data[13] * self._data[5]
            + other._data[14] * self._data[9]
            + other._data[15] * self._data[13]
        )
        res._data[14] = (
            other._data[12] * self._data[2]
            + other._data[13] * self._data[6]
            + other._data[14] * self._data[10]
            + other._data[15] * self._data[14]
        )
        res._data[15] = (
            other._data[12] * self._data[3]
            + other._data[13] * self._data[7]
            + other._data[14] * self._data[11]
            + other._data[15] * self._data[15]
        )

        return res


class _Matrix4Methods():
    """
    4 by 4 Matrix class which allows [i, j] indexing
    """

    def __str__(self):
        lst = (
            f"{self[0,0]}\t\t{self[0,1]}\t\t{self[0,2]}\t\t{self[0,3]}",
            f"{self[1,0]}\t\t{self[1,1]}\t\t{self[1,2]}\t\t{self[1,3]}",
            f"{self[2,0]}\t\t{self[2,1]}\t\t{self[2,2]}\t\t{self[2,3]}",
            f"{self[3,0]}\t\t{self[3,1]}\t\t{self[3,2]}\t\t{self[3,3]}",
        )
        return "\n".join(lst)

    def __mul__(self, other):
        """
        Multiplies matrix with matrix or matrix with vector
        """
        if isinstance(other, (_PyMatrix4Base, Matrix4)):
            return self @ other            
        if isinstance(other, IVec):
            res = [0, 0, 0, 0]
            if len(other) != 4:
                other = Vec(other.as_n_d(4))
                other[3] = 1

            for i in range(4):
                res[i] = (
                    self[0, i] * other[0]
                    + self[1, i] * other[1]
                    + self[2, i] * other[2]
                    + self[3, i] * other[3]
                )
            return IVec(res)

        return NotImplemented

    @classmethod
    def translation_matrix(cls, x, y, z):
        """
        Creates matrix that translates vectors by *x*, *y*, *z*
        """
        mat = cls(IDENTITY)
        mat[3, 0] = x
        mat[3, 1] = y
        mat[3, 2] = z
        return mat

    @classmethod
    def look_at(cls, eye: Vec, center: Vec, up: Vec):
        """
        Generates a look at matrix from *eye* to *center* with *up* up vector
        """

        res = cls(IDENTITY)

        f = (center - eye).normalized()
        u = up.normalized()
        s = f.cross(u)
        if s.len_sqr() > 0:
            s = s.normalized()
        u = s.cross(f)

        res[0, 0] = s.x
        res[1, 0] = s.y
        res[2, 0] = s.z
        res[0, 1] = u.x
        res[1, 1] = u.y
        res[2, 1] = u.z
        res[0, 2] = -f.x
        res[1, 2] = -f.y
        res[2, 2] = -f.z
        res[3, 0] = -s.dot(eye)
        res[3, 1] = -u.dot(eye)
        res[3, 2] = f.dot(eye)

        return res

    @classmethod
    def orthogonal_projection(cls, l, r, b, t, n=-0.1, f=100):
        """
        Creates orthogonal projection
        """
        mat = Matrix4([
            2/(r-l), 0, 0, 0,
            0, 2/(t-b), 0, 0,
            0, 0, -2/(f-n), 0,
            -(r+l)/(r-l), -(t+b)/(t-b), -(f+n)/(f-n), 1
        ])
        return mat

    @classmethod
    def perspective_projection(cls, fov, ratio, near, far):
        """
        Creates perspective projection matrix from *fov*, *ratio*(width/height) and \
        culling planes(*near* and *far*)
        """
        bt = near * math.tan(fov * math.pi / 360.0)
        lr = bt * ratio

        return cls.perspective_projection_lrbtnf(-lr, lr, -bt, bt, near, far)

    @classmethod
    def perspective_projection_lrbtnf(cls, left, right, bottom, top, near, far):
        """
        Creates perspective projection from boundaries
        """
        A = (right + left) / (right - left)
        B = (top + bottom) / (top - bottom)
        C = -(far + near) / (far - near)
        D = -2 * far * near / (far - near)
        E = 2 * near / (right - left)
        F = 2 * near / (top - bottom)

        return cls([E, 0, 0, 0, 0, F, 0, 0, A, B, C, -1, 0, 0, D, 0])  # TODO

    @classmethod
    def rotation_euler(cls, pitch, roll, yaw):
        """
        Creates rotation matrix from 3 angles(*pitch*, *roll* and *yaw*)
        """

        sP = math.sin(pitch)
        cP = math.cos(pitch)
        sR = math.sin(roll)
        cR = math.cos(roll)
        sY = math.sin(yaw)
        cY = math.cos(yaw)

        return cls(
            [
                cY * cP,
                -cY * sP * cR + sY * sR,
                cY * sP * sR + sY * cR,
                0,
                sP,
                cP * cR,
                -cP * sR,
                0,
                -sY * cP,
                sY * sP * cR + cY * sR,
                -sY * sP * sR + cY * cR,
                0,
                0,
                0,
                0,
                1,
            ]
        )
    
    @classmethod
    def scale_matrix(cls, by):
        """
        Creates matrix that scales by *by*
        """
        return Matrix4([by, 0, 0, 0, 0, by, 0, 0, 0, 0, by, 0, 0, 0, 0, 1])
    
    def transpose(self):
        return Matrix4([
            self[0,0], self[1,0], self[2,0], self[3,0],
            self[0,1], self[1,1], self[2,1], self[3,1],
            self[0,2], self[1,2], self[2,2], self[3,2],
            self[0,3], self[1,3], self[2,3], self[3,3],
        ])        

    def inverse(self):
        m = [[self[i,j] for j in range(4)] for i in range(4)]
        r = []
        res = _inv(m)
        if res is None:
            return None
        for c in res:
            r.extend(c)
        return Matrix4(r)

    def __bytes__(self):
        return self.bytes()


class PyMatrix4(_PyMatrix4Base, _Matrix4Methods):
    pass


Matrix4 = PyMatrix4

try:
    from qlibs_cyan.math.mat4 import Matrix4 as _CMatrix4Base
except ImportError:
    print("It appears that Qlibs Cyan is not installed, performace will be worse without it", file=sys.stderr) #TODO think of something better
else:
    class Matrix4(_CMatrix4Base, _Matrix4Methods):
        def __init__(self, data=None):
            if data is not None:
                ind = 0
                for i in range(4):
                    for j in range(4):
                        self[i,j] = data[ind]
                        ind += 1
