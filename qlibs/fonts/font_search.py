import sys
from os.path import exists
from ..resources.resource_loader import get_res_path

def find_reasonable_font():
    """Try to return system font path, or some other font"""
    if sys.platform.startswith("win"):
        #path = "c:/windows/fonts/arial"
        raise NotImplementedError() #TODO
    else:
        with open(get_res_path("qlibs/text/linux_font_list")) as file:
            for path in file:
                if exists(path[:-1]):
                    return path[:-1]
    return None
        