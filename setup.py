import os
from sys import platform
from pathlib import Path
from jinja2 import Template
from pkg_resources import parse_version
from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext as _build_ext

lib_name = 'monetdbe'
monetdb_branch = os.environ.get("MONETDB_BRANCH", "default")
newer_then_jul2021 = monetdb_branch.lower() not in ("oct2020", "jul2021")
win32 = platform == 'win32'


with open('monetdbe/_cffi/embed.h.j2', 'r') as f:
    content = f.read()
    template = Template(content)
    out = template.render(win32=win32, newer_then_jul2021=newer_then_jul2021)
    with open('monetdbe/_cffi/embed.h', 'w') as f:
        f.write(out)


def get_monetdbe_paths():
    """Obtain the paths for compiling and linking with monetdbe
    """
    libraries = [lib_name]
    library_dirs = []
    include_dirs = ['monetdbe/_cffi']
    extra_link_args = []

    include_dir = os.environ.get("MONETDBE_INCLUDE_PATH")
    library_dir = os.environ.get("MONETDBE_LIBRARY_PATH")
    if include_dir and library_dir:
        return {
            "include_dirs": include_dirs + [include_dir],
            "library_dirs": [library_dir],
            "libraries": libraries,
        }


    return {
        "include_dirs": include_dirs,
        "library_dirs": library_dirs,
        "libraries": libraries,
        "extra_link_args": extra_link_args,
    }


with open("README.md", "r") as fh:
    long_description = fh.read()

tests_require = [
    'pytest',
    'mypy',
    'pycodestyle',
    'data-science-types',
    'types-setuptools',
    'types-pkg_resources',
    'types-Jinja2',
    'typing-extensions',
    'pymonetdb',
]

extras_require = {
    'test': tests_require,
    'doc': ['sphinx', 'sphinx_rtd_theme'],
}

packages = find_packages(exclude=['tests', 'tests.test_lite'])

if win32:
    package_data = {"monetdbe": ["*.dll"]}
else:
    package_data = {}

ext_options = get_monetdbe_paths()
ext_modules = [
    Extension(
        'monetdbe._lowlevel',
        sources=['monetdbe/_cffi/native_utilities.c'],
        language='c',
        **ext_options,
    )
]

setup(
    name="monetdbe",
    version="0.11",
    author="Gijs Molenaar",
    author_email="gijs@pythonic.nl",
    description="MonetDBe - the Python embedded MonetDB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/monetdBSolutions/MonetDBe-Python/",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Database :: Front-Ends",
    ],
    python_requires='>=3.7',
    setup_requires=["cffi>=1.0.0", "Jinja2"],
    extras_require=extras_require,
    install_requires=["cffi>=1.0.0", "numpy", "pandas"],
    tests_require=tests_require,
    test_suite="tests",
    package_data=package_data,
    ext_modules=ext_modules,
)
