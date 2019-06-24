"""
  Matrix module
"""

from array import array
from ctypes import string_at
import math

from .vec import IVec, MVec as Vec

ZEROS_16 = [0] * 16
IDENTITY = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]


class Matrix4:
    __slots__ = ("_data",)
    """
    4 by 4 Matrix class which allows [i, j] indexing
    """

    def __init__(self, data=None, dtype="f", raw_init=None):
        """
        Initialize matrix with 16 elements array (*data*) of *dtype* type
        """
        if raw_init is not None:
            self._data = raw_init
            return
        
        if data is not None:
            self._data = array(dtype, data)
        else:
            self._data = array(dtype, ZEROS_16)

    def __getitem__(self, key):
        x, y = key
        assert 0 <= x < 4 and 0 <= y < 4
        return self._data[x * 4 + y]

    def __setitem__(self, key, value):
        x, y = key
        assert 0 <= x < 4 and 0 <= y < 4
        self._data[x * 4 + y] = value

    def __str__(self):
        lst = (
            f"{self[0,0]}\t\t{self[0,1]}\t\t{self[0,2]}\t\t{self[0,3]}",
            f"{self[1,0]}\t\t{self[1,1]}\t\t{self[1,2]}\t\t{self[1,3]}",
            f"{self[2,0]}\t\t{self[2,1]}\t\t{self[2,2]}\t\t{self[2,3]}",
            f"{self[3,0]}\t\t{self[3,1]}\t\t{self[3,2]}\t\t{self[3,3]}",
        )
        return "\n".join(lst)

    def __repr__(self):
        if list(self._data) == IDENTITY:
            return "Matrix4(IDENTITY)"
        if list(self._data) == ZEROS_16:
            return "Matrix4(ZEROS_16)"
        return f"Matrix4({list(self._data)})"

    def __mul__(self, other):
        """
        Multiplies matrix with matrix or matrix with vector
        """
        if isinstance(other, Matrix4):
            res = Matrix4()

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

        if isinstance(other, IVec):
            res = [0, 0, 0, 0]
            if len(other) != 4:
                other = other.as_n_d(4)
                other[3] = 1

            for i in range(4):
                res[i] = (
                    self[i, 0] * other[0]
                    + self[i, 1] * other[1]
                    + self[i, 2] * other[2]
                    + self[i, 3] * other[3]
                )
            return IVec(res)

        return NotImplemented

    def __eq__(self, other):
        return self._data == other._data

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
        Creates rotation matrix from 3 angles(*pith*, *roll* and *yaw*)
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
    
    def bytes(self, dtype="f"):
        """
        Converts internal array to bytes
        """
        if isinstance(self._data, array):
            assert self._data.typecode == dtype
            return self._data.tobytes()
        else:
            return string_at(self._data, 64)
