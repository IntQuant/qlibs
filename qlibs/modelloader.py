import sys
import pathlib
from enum import Enum
from array import array

try:
    from vec import Vec
except ImportError:
    from .vec import Vec

def int_or_none(value):
    try:
        return int(value)
    except ValueError:
        return None

def index_or_none(value):
    try:
        v = int(value)
        if v > 0:
            return v - 1
        else:
            return v
    except ValueError:
        return None

class OBJIndex(Enum):
    VX = 0
    VTX = 1
    VNX = 2
    VY = 3
    VTY = 4
    VNY = 5
    VZ = 6
    VTZ = 7
    VNZ = 8

OBJ_VERTEX = [OBJIndex.VX, OBJIndex.VY, OBJIndex.VZ]
OBJ_TEXTURE = [OBJIndex.VTX, OBJIndex.VTY, OBJIndex.VTZ]
OBJ_NORMAL = [OBJIndex.VNX, OBJIndex.VNY, OBJIndex.VNZ]

class Material():
    def __init__(self):
        self.raw_params = dict()
        self.prc_params = dict()

class MTLLoader():
    def __init__(self):
        self.materials = dict()
        self.current = None
    
    def get_mat(self, name=None):
        if name is None:
            name = self.current
        
        v = self.materials.get(name)
        if v is None:
            mt = Material()
            self.materials[name] = mt
            return mt
        else:
            return v
    
    def load_file(self, f):
        for line in f:
            if line.startswith("#"):
                continue
            #print(line)
            
            try:
                param, opt = line.split(maxsplit=1)
            except ValueError:
                print("Could not split line while parsing mtl file", file=sys.stderr)
                continue
            
            if param == "newmtl":
                self.current = opt
            else:
                self.get_mat().raw_params[param] = opt
            
            
    
    def load_path(self, path):
        with open(path, 'r') as f:
            return self.load_file(f)

class SubOBJ():
    def __init__(self):
        self.f = []

class OBJ():
    def __init__(self):
        pass
        

class OBJLoader(): #TODO: support for multiple objects
    def __init__(self):
        self.v = []
        
        self.vt = []
        self.vn = []
        
        self.sub_obj = dict()
        
        self.materials = dict()
        
        self.current_material = None
        
        self.loads_from = ""
    
    def get_sub_obj(self, material=None):
        if material is None:
            material = self.current_material
        
        v = self.sub_obj.get(material)
        if v is not None:
            return v
        else:
            v = SubOBJ()
            self.sub_obj[material] = v
            return v
            
    
    def load_file(self, f):
        mtl_loader = MTLLoader()
        
        for line in f:
            if line.startswith('#'):
                continue
            #print(line)
            op, *params = line.split()
            
            if op == "v":
                t = tuple(map(float, params))
                assert len(t) == 3
                self.v.append(t)
            elif op == "vt":
                t = tuple(map(float, params))
                assert len(t) == 2
                self.vt.append(t)
            elif op == "vn":
                t = Vec(map(float, params))
                assert len(t) == 3
                t.normalize()
                self.vn.append(t)
            elif op == "f":
                t = []
                for p in params:
                    t.extend(map(index_or_none, p.split('/')))
                self.get_sub_obj().f.append(t)
            elif op == "usemtl":
                self.current_material = params[0]
                #print(f"Changed material to {params[0]}", file=sys.stderr)
            elif op == "mtllib":
                path = pathlib.Path(params[0])
                print(path)
                if path.is_absolute():
                    pass
                else:
                    #print("converted to absolute")
                    path = pathlib.Path(self.loads_from).parent.joinpath(path)
                #print(f"Loading mtl from {path}")
                mtl_loader.load_path(path)
                
            else:
                print(f"Unsapported op {op}", file=sys.stderr)
        self.materials.update(mtl_loader.materials)
                
    def load_path(self, path):
        self.loads_from = path
        with open(path, "r") as f:
            return self.load_file(f)
    
    def resolve(self, *form, material=None):
        res = array("f")
        
        if len(form) == 0:
            
            form = (OBJIndex.VX, OBJIndex.VNX, OBJIndex.VTX,
                    OBJIndex.VY, OBJIndex.VNY, OBJIndex.VTY,
                    OBJIndex.VZ, OBJIndex.VNZ, OBJIndex.VTZ)
        
        for face in self.get_sub_obj().f:
            for f in form:
                if f in OBJ_VERTEX:
                    res.extend(self.v[face[f.value]])
                elif f in OBJ_TEXTURE:
                    res.extend(self.vt[face[f.value]])
                elif f in OBJ_NORMAL:
                    res.extend(self.vn[face[f.value]])
                else:
                    raise ValueError("Wrong format")
        return res
        
            
            
