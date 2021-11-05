from subprocess import call

with open("version.txt", "r") as f:
    version = f.read().strip('\n')

print(f"Version: {version}")

print("Updating __init__.py...")
with open("qlibs/__init__.py", "w") as file:
    print("#Note: autogenerated", file=file)
    print(f"__version__ = '{version}'", file=file)

print("Updating setup.py")
with open("setup.py", "r") as file:
    lines = file.readlines()
lines[0] = f"version = '{version}'\n"
with open("setup.py", "w") as file:
    print(*lines, file=file, sep="")

print("Building sdist...")
ret = call(["python3", "setup.py", "sdist"])
if ret != 0:
    print("Build failed")
    exit(ret)

print("Uploading...")
filename = f"dist/qlibs-{version}.tar.gz"
ret = call(["twine", "upload", filename])
if ret != 0:
    print("Upload failed")
    exit(ret)

print("Done!")
