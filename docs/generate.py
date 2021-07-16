from glob import glob
import os
from os.path import exists
from os import chdir, makedirs
import subprocess


base_index = """
Welcome to QLibs's documentation!
=================================

.. py:module:: qlibs

.. toctree::
   :maxdepth: 2
   
   reference/index.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
"""

if not exists("setup.py"):
    exit(1)

def gen_index(title, refs, file, title_char="-"):
    print(title, file=file)
    print(title_char*len(title), file=file)
    print(file=file)
    #print(".. py:module:: qlibs", file=file)
    print(file=file)
    print(".. toctree::", file=file)
    print("   :maxdepth: 2", file=file)
    print(file=file)
    for ref in refs:
        if not ref.endswith(".rst"):
            ref = ref + "/index.rst"
        print("  ", ref, file=file)


module_list = glob("qlibs/**/*.py", recursive=True)
chdir("docs")
base_ref = "reference"
makedirs(base_ref, exist_ok=True)
walked_dirs = set()

for module in module_list:
    module = module.replace("/", ".")
    if module.endswith(".__init__.py"):
        continue
    #module = module.removesuffix(".__init__.py")
    module = module.removesuffix(".py")
    #print(module)
    docpath = module.split(".", maxsplit=1)[1].replace(".", "/", 1)
    docdir = docpath.split("/", maxsplit=1)[0]
    docdir = os.path.join(base_ref, docdir)
    docpath = os.path.join(base_ref, docpath) + ".rst"
    #print(docdir, docpath)
    walked_dirs.add(docdir)
    makedirs(docdir, exist_ok=True)
    with open(docpath, "w") as file:
        title = f"Module {module}"
        print(title, file=file)
        print("~"*len(title), file=file)
        print(file=file)
        print(f".. py:currentmodule:: {module}", file=file)
        print(file=file)
        print(f".. automodule:: {module}", file=file)
        print("   :members:", file=file)
        print("   :undoc-members:", file=file)

print(walked_dirs)
for wdir in walked_dirs:
    lst = os.listdir(wdir)
    try:
        lst.remove("index.rst")
    except ValueError:
        pass
    lst.sort()
    print(wdir, lst)
    title = wdir.rsplit("/", maxsplit=1)[1].capitalize() + " reference"
    with open(os.path.join(wdir, "index.rst"), "w") as file:
        gen_index(title, lst, file)

lst = os.listdir("reference")
try:
    lst.remove("index.rst")
except ValueError:
    pass
print(lst)
with open("reference/index.rst", "w") as file:
    gen_index("Reference", lst, file, title_char="=")

with open("index.rst", "w") as file:
    file.write(base_index)

subprocess.run(["make", "clean"])
subprocess.run(["make", "html"])