import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="qlibs",
    version="0.2.1",
    author="IQuant",
    author_email="quant3234@gmail.com",
    description="Networking, gui, math and more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/IntQuant/qlibs/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    install_requires=["moderngl", "glfw"],
    extras_require={
        "full": ["pillow", "freetype-py"]
    },
)
