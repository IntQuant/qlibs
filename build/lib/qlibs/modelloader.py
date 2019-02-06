"""
  Module for loading 3D models
"""

import sys
import pathlib
from enum import Enum
from array import array


from .vec import Vec

try:
    from tqdm import tqdm
except ImportError:

    def tqdm(x, **kwargs):
        return x


def int_or_none(value):
    """
      Returns int or none if int could not be converted
    """
    try:
        return int(value)
    except ValueError:
        return None


def index_or_none(value):
    """
      Maps OBJ file index to python 0-index scheme
    """
    try:
        v = int(value)
        if v > 0:
            return v - 1
        else:
            return v
    except ValueError:
        return None


class OBJIndex(Enum):
    """
      Parameters to specify data order
    """

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

FORMAT_TEXTURES = (
    OBJIndex.VX,
    OBJIndex.VNX,
    OBJIndex.VTX,
    OBJIndex.VY,
    OBJIndex.VNY,
    OBJIndex.VTY,
    OBJIndex.VZ,
    OBJIndex.VNZ,
    OBJIndex.VTZ,
)
FORMAT_NO_TEXTURES = (
    OBJIndex.VX,
    OBJIndex.VNX,
    OBJIndex.VY,
    OBJIndex.VNY,
    OBJIndex.VZ,
    OBJIndex.VNZ,
)

MATERIAL_LIGHT_PROPERTIES = ("Ka", "Kd", "Ks")
MATERIAL_LIGHT_PROPERTIES_MAP = ("map_Ka", "map_Kd", "map_Ks")


def check_has_textures(face):
    """
      Checks if object's face has all textures
    """
    return all(face[i.value] is not None for i in OBJ_TEXTURE)


def check_has_no_textures(face):
    """
      Checks if object's face does not have all textures
    """
    return not check_has_textures(face)


class Material:
    """
      Object that describes material properties
    """

    def __init__(self, name):
        self.raw_params = dict()
        self.prc_params = dict()
        self.name = name
        self.processed = False

    def process(self, ensure_processing=False):
        if (not ensure_processing) and self.processed:
            return
        self.processed = True

        # for p in MATERIAL_LIGHT_PROPERTIES:
        #    self.prc_params[p] = int(self.raw_params[p])

        for p in MATERIAL_LIGHT_PROPERTIES_MAP:
            self.prc_params[p] = self.raw_params.get(p)
        # TODO - add texture processing


class MTLLoader:
    """
      .mtl file loader
    """

    def __init__(self):
        self.materials = dict()
        self.current = None

    def get_mat(self, name=None):
        if name is None:
            name = self.current

        v = self.materials.get(name)
        if v is None:
            mt = Material(name)
            self.materials[name] = mt
            return mt
        else:
            return v

    def load_file(self, f):
        for line in f:
            if line.startswith("#"):
                continue
            try:
                param, opt = line.split(maxsplit=1)
            except ValueError:
                print("Could not split line while parsing mtl file", file=sys.stderr)
                continue

            if param == "newmtl":
                self.current = opt.rstrip("\n")
            else:
                self.get_mat().raw_params[param] = opt.rstrip("\n")

    def load_path(self, path):
        with open(path, "r") as f:
            return self.load_file(f)


class SubOBJ:
    """
      Part of object with one material
    """

    def __init__(self, name):
        self.f = []
        self.mat_name = name


class OBJ:
    """
      Loaded object class
    """

    def __init__(self, name, materials):
        self.v = []

        self.vt = []
        self.vn = []

        self.sub_obj = dict()
        self.materials = materials

        self.name = name

    def get_sub_obj(self, material):
        v = self.sub_obj.get(material)
        if v is not None:
            return v
        else:
            v = SubOBJ(material)
            self.sub_obj[material] = v
            return v

    def iter_materials_textured(self, *form):
        """
          Iterate over textured material faces
        """

        for sub_obj_key in self.sub_obj:
            yield (
                self.sub_obj[sub_obj_key],
                self.resolve(*form, material=sub_obj_key, filter_by=check_has_textures),
            )

    def iter_materials_non_textured(self, *form):
        """
          Iterate over non textured mateial faces
        """

        if len(form) == 0:
            form = FORMAT_NO_TEXTURES

        for sub_obj_key in self.sub_obj:
            yield (
                self.sub_obj[sub_obj_key],
                self.resolve(
                    *form, material=sub_obj_key, filter_by=check_has_no_textures
                ),
            )

    def resolve(self, *form, filter_by=lambda x: True, material=None):
        """
          Resolves faces to parameter array defined by *form* format
        """

        res = array("f")

        if material is None:
            material = list(self.sub_obj.keys())[0]

        if len(form) == 0:

            form = FORMAT_TEXTURES

        for face in self.get_sub_obj(material).f:
            if not filter_by(face):
                continue

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


class OBJLoader:
    """
      Loads object files
    """

    def __init__(self):

        self.objects = dict()
        self.current_object = None

        self.materials = dict()
        self.current_material = None

        self.loads_from = ""

    def get_obj(self, name=None):
        if name is None:
            name = self.current_object

        v = self.objects.get(name)
        if v is not None:
            return v
        else:
            v = OBJ(name, materials=self.materials)
            self.objects[name] = v
            return v

    def get_sub_obj(self, name=None, material=None):
        o = self.get_obj(name=name)

        if material is None:
            material = self.current_material

        return o.get_sub_obj(material)

    def load_file(self, f, triangulate=True):
        """
          Loads models from file object
        """

        mtl_loader = MTLLoader()

        for line in f:
            if line.startswith("#"):
                continue
            try:
                op, *params = line.split()
            except ValueError:
                continue

            if op == "v":
                t = tuple(map(float, params))
                assert len(t) == 3
                self.get_obj().v.append(t)
            elif op == "vt":
                t = tuple(map(float, params))
                assert len(t) == 2
                self.get_obj().vt.append(t)
            elif op == "vn":
                t = Vec(map(float, params))
                assert len(t) == 3
                t.normalize()
                self.get_obj().vn.append(t)
            elif op == "f":

                if triangulate:
                    params = list(
                        map(lambda x: tuple(map(index_or_none, x.split("/"))), params)
                    )
                    for i in range(len(params) - 2):
                        t = []
                        t.extend(params[0])
                        t.extend(params[i + 1])
                        t.extend(params[i + 2])
                        self.get_sub_obj().f.append(t)
                else:
                    t = []
                    for p in params:
                        t.extend(map(index_or_none, p.split("/")))
                    self.get_sub_obj().f.append(t)
            elif op == "usemtl":
                self.current_material = params[0]
            elif op == "mtllib":
                path = pathlib.Path(params[0])
                print(path)
                if path.is_absolute():
                    pass
                else:
                    path = pathlib.Path(self.loads_from).parent.joinpath(path)
                mtl_loader.load_path(path)
            elif op == "o":
                self.current_object = params[0]

            else:
                print(f"Unsapported op {op}", file=sys.stderr)
        self.materials.update(mtl_loader.materials)

    def load_path(self, path):
        """
          Loads models from *path*
        """
        self.loads_from = path
        with open(path, "r") as f:
            return self.load_file(f)
