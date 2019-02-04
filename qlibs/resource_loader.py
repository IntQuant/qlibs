import sys
import os.path

try:
    import moderngl
except ImportError:
    print("Could not import moderngl", file=sys.stderr)

from .util import dict_cache

try:
    from PIL import Image
except ImportError:
    print("Could not import PIL(pillow)", file=sys.stderr)


search_locations = []


def get_lib_res_path():
    return os.path.join(__file__[: -len("resource_loader.py")], "resources")


search_locations.append(get_lib_res_path())


def get_res_path(path):
    for c_path in search_locations:
        cand_path = os.path.join(c_path, path)
        if os.path.exists(cand_path):
            return cand_path
    return os.path.join(get_lib_res_path(), path)


def get_res_data(path):
    with open(get_res_path(path), "r") as f:
        return f.read()


@dict_cache
def get_res_texture(r_path, ctx):

    path = get_res_path(r_path)
    # print(path)
    img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")

    txt = ctx.texture(img.size, 3, img.tobytes())
    txt.build_mipmaps()
    return txt


def ensure_sdl2_install():
    os.environ["PYSDL2_DLL_PATH"] = get_res_path("dll")
