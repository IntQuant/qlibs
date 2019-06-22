import sys
import os.path

try:
    import moderngl
except ImportError:
    print("Could not import moderngl", file=sys.stderr)

from .util import dict_cache, weak_ref_cache

try:
    from PIL import Image
except ImportError:
    print("Could not import PIL(pillow)", file=sys.stderr)


search_locations = []

class ImageData:
    def __init__(self, size, data):
        self.size = size
        self.data = data

def get_lib_res_path():
    return os.path.join(__file__[: -len("resource_loader.py")], "resources")


search_locations.append(get_lib_res_path())


def get_res_path(path):
    for c_path in search_locations:
        cand_path = os.path.join(c_path, path)
        if os.path.exists(cand_path):
            return cand_path
    raise FileNotFoundError(f"Can't find {path}")


def get_res_data(path):
    with open(get_res_path(path), "r") as f:
        return f.read()

@weak_ref_cache
def get_image_data(r_path):
    path = get_res_path(r_path)
    img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
    return ImageData(img.size, img.tobytes())

@dict_cache
def get_res_texture(r_path, ctx):
    path = get_res_path(r_path)
    img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
    txt = ctx.texture(img.size, 3, img.tobytes())
    txt.build_mipmaps()
    return txt
