from array import array
import math
try:
    from vec import Vec
except ImportError:
    from .vec import Vec

ZEROS_16 = [0] * 16

IDENTITY = [1, 0, 0, 0, 
            0, 1, 0, 0,
            0, 0, 1, 0,
            0, 0, 0, 1]

class Matrix4():
    def __init__(self, data=None, dtype="f"):
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
        lst = (f"{self[0,0]}\t\t{self[0,1]}\t\t{self[0,2]}\t\t{self[0,3]}",
               f"{self[1,0]}\t\t{self[1,1]}\t\t{self[1,2]}\t\t{self[1,3]}",
               f"{self[2,0]}\t\t{self[2,1]}\t\t{self[2,2]}\t\t{self[2,3]}",
               f"{self[3,0]}\t\t{self[3,1]}\t\t{self[3,2]}\t\t{self[3,3]}")
        return "\n".join(lst)
        
    
    def __repr__(self):
        return f"Matrix4({list(self._data)})"
    
    def __mul__(self, other):
        if isinstance(other, Matrix4):
            res = Matrix4() #TODO ~~- flatter loops~~ -make working
            for x in range(4):
                for y in range(4):
                    res[x, y] = sum((other[x, i] * self[i, y] for i in range(4)))
                    
                         
                        
                    
            return res
        
        if isinstance(other, Vec):
            res = Vec(0, 0, 0, 0)
            if len(other) != 4:
                other = other.as_n_d(4)
                other[3] = 1
            
            for i in range(4):
                res[i] = self[i, 0] * other[0] + self[i, 1] * other[1] + self[i, 2] * other[2] + self[i, 3] * other[3]
            return res
        
        return NotImplemented
    
    def __eq__(self, other):
        return self._data == other._data                

    @classmethod
    def translation_matrix(cls, x, y, z):
        mat = cls(IDENTITY)
        mat[3, 0] = x
        mat[3, 1] = y
        mat[3, 2] = z
        return mat
    
    @classmethod    
    def look_at(cls, eye: Vec, center: Vec, up: Vec):
        res = cls(IDENTITY)
        
        '''
        vec3  f = normalize(center - eye);
        vec3  u = normalize(up);
        vec3  s = normalize(cross(f, u));
        u = cross(s, f);'''
        
        f = center - eye; f.normalize()
        u = Vec(up);      u.normalize()
        s = f.cross(u);   s.normalize()
        u = s.cross(f)
        

        res[0, 0] = s.x
        res[1, 0] = s.y
        res[2, 0] = s.z
        res[0, 1] = u.x
        res[1, 1] = u.y
        res[2, 1] = u.z
        res[0, 2] =-f.x
        res[1, 2] =-f.y
        res[2, 2] =-f.z
        res[3, 0] =-s.dot(eye)
        res[3, 1] =-u.dot(eye)
        res[3, 2] = f.dot(eye)
        return res
    
    @classmethod
    def orthogonal_projection(cls, fov, ratio, n, f): #TODO
        """
          fov - field of view
          ratio - width/height
          Near
          Far
        """
        r = math.cos(math.degrees(fov / 2)) * n #TODO
        t = r / ratio
        
        mat = cls(IDENTITY)
        mat[0, 0] = 1 / r
        mat[1, 1] = 1 / t
        mat[2, 2] = -2/(f-n)
        mat[2, 3] = -(f+n)/(f-n)
        
        return mat
    
    @classmethod
    def perspective_projection(cls, fov, ratio, near, far):
        """
          fov - field of view
          ratio - width/height
          Near
          Far
        """
        bt = near * math.tan(fov * math.pi / 360.0)
        lr = bt * ratio
        
        return cls.perspective_projection_lrbtnf(-lr, lr, -bt, bt, near, far)
        
    @classmethod    
    def perspective_projection_lrbtnf(cls, left, right, bottom, top, near, far):    
        A = (right + left) / (right - left)
        B = (top + bottom) / (top - bottom)
        C = -(far + near) / (far - near)
        D = -2 * far * near / (far - near)
        E = 2 * near / (right - left)
        F = 2 * near / (top - bottom)
        
        return cls([E, 0, 0, 0, 0, F, 0, 0, A, B, C, -1, 0, 0, D, 0]) #TODO
    
    @classmethod
    def rotation_euler(cls, pitch, roll, yaw):
        sP = math.sin(pitch)
        cP = math.cos(pitch)
        sR = math.sin(roll)
        cR = math.cos(roll)
        sY = math.sin(yaw)
        cY = math.cos(yaw)
        
        return cls([cY * cP, -cY * sP * cR + sY * sR, cY * sP * sR + sY * cR, 0, sP, cP * cR, -cP * sR, 0, sY * cP, sY * sP * cR + cY * sR, -sY * sP * sR + cY * cR, 0, 0, 0, 0, 1])
    
    def bytes_dtype(self, dtype="f") :
        assert self._data.typecode == dtype
        return self._data.tobytes()
        
        
