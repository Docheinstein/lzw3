import os
from setuptools import setup, find_packages


def read(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as f:
        return f.read()


setup(
    name="lzw3",
    version="0.3",

    # Requires python3.5
    python_requires=">=3.5",

    # Automatically import lzw3 packages
    packages=find_packages(),

    # Include the files specified in MANIFEST.in in the release archive
    include_package_data=True,

    # Scripts to install to the user executable path.
    # Note that this might be something like /home/user/.local/bin
    # which in Debian distributions is not included in $PATH.
    # If you want to use just "compress" or "uncompress", you should add that
    # path to your $PATH.
    scripts=["scripts/compress", "scripts/uncompress"],

    # Tests
    test_suite="tests",

    # Metadata
    author="Stefano Dottore",
    author_email="docheinstein@gmail.com",
    description="Compressor and decompressor for arbitrary files that use LZW algorithm",
    long_description=read('README.rst'),
    license="MIT",
    keywords="lzw lzw3 compressor decompressor compression compress uncompress",
    url="https://github.com/Docheinstein/lzw3"
)
