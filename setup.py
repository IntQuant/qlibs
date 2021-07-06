import setuptools
from setuptools import Extension
import traceback

with open("README.md", "r") as fh:
    long_description = fh.read()

def do_setup(ext_modules):
    setuptools.setup(
        name="qlibs",
        version="0.5.4",
        author="IQuant",
        author_email="quant3234@gmail.com",
        description="Networking, gui, math and more",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://bitbucket.org/IntQuant/qlibs/",
        packages=setuptools.find_packages(),
        license="MIT",
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        include_package_data=True,
        install_requires=["moderngl", "glfw"],
        extras_require={
            "full": ["pillow", "freetype-py"],
            "cyan": ["qlibs-cyan==0.1.0"],
        },
        ext_modules=ext_modules,
        zip_safe=False,
    )

#do_setup([Extension("qlibs.math.mat4", ["qlibs/math/cmatrix/mat4.c"])])
do_setup([])
