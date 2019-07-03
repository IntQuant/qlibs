import sys
import os.path

from ..util import dict_cache, weak_ref_cache

try:
    from PIL import Image
except ImportError:
    print("Could not import PIL(pillow), image loading is unavailable", file=sys.stderr)

loader = None


class ImageData:
    def __init__(self, size, data):
        self.size = size
        self.data = data


class Loader:
    def resolve(self, path):
        raise NotImplementedError()

    def handle_prefix(self, path, prefix):
        if prefix is None:
            return path
        if path.startswith(prefix):
            path = path[len(prefix):]
            return path


class SearchLocationLoader(Loader):
    def __init__(self, location, prefix=None):
        self.location = location
        if prefix is None or prefix.endswith("/"):
            self.prefix = prefix
        else:
            raise ValueError("Prefix should end with '/'")
    
    def resolve(self, path):
        path = self.handle_prefix(path, self.prefix)
        if path is None:
            return None
        path = os.path.join(self.location, path)
        if os.path.exists(path):
            return path
    

class MergerLoader(Loader):
    def __init__(self, loaders, prefix=None):
        self.loaders = loaders
        if prefix is None or prefix.endswith("/"):
            self.prefix = prefix
        else:
            raise ValueError("Prefix should end with '/'")
    
    def resolve(self, path):
        path = self.handle_prefix(path, self.prefix)
        if path is None:
            return None
        for loader in self.loaders:
            resolved = loader.resolve(path)
            if resolved is not None:
                return resolved

def get_lib_res_path():
    return os.path.join(os.path.dirname(__file__), "storage")


def get_res_path(path):
    #for c_path in search_locations:
    #    cand_path = os.path.join(c_path, path)
    #    if os.path.exists(cand_path):
    #        return cand_path
    resolved = loader.resolve(path)
    if resolved is None:
        raise FileNotFoundError(f"Can't find {path}")
    else:
        return resolved


def get_res_data(path):
    with open(get_res_path(path), "r") as f:
        return f.read()

@weak_ref_cache
def get_image_data(r_path, mode="RGB"):
    if os.path.isabs(r_path):
        path = r_path
    else:
        path = get_res_path(r_path)
    img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM).convert(mode)
    return ImageData(img.size, img.tobytes())

@dict_cache
def get_res_texture(r_path, ctx):
    path = get_res_path(r_path)
    img = Image.open(path).transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
    txt = ctx.texture(img.size, 3, img.tobytes())
    txt.build_mipmaps()
    return txt

loader = MergerLoader([])

def add_loader(loader_):
    loader.loaders.append(loader_)

loader.loaders.append(SearchLocationLoader(get_lib_res_path(), prefix="qlibs/"))


