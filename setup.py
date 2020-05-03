from setuptools import setup

with open("README.md") as file_object:
    description = file_object.read()

setup(
    name="blenderer",
    version="0.0.1",
    author="Mandeep",
    author_email="mandeep@keemail.me",
    url="https://github.com/mandeep/blenderer",
    long_description=description,
    long_description_content_type="text/markdown",
    description="Render scripts for use in Blender 2.8.",
    license="MIT",
    packages=["blenderer"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    data_files=[("", ["LICENSE"])],
)
