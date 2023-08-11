from setuptools import find_packages, setup
from sys import platform
from setuptools.command.build_ext import build_ext as _build_ext


def get_monetdbe_paths():
    import os
    """Obtain the paths for compiling and linking with monetdbe """

    include_dir = os.environ.get("MONETDBE_INCLUDE_PATH")
    library_dir = os.environ.get("MONETDBE_LIBRARY_PATH")

    return {
        "include_dir": include_dir,
        "library_dir": library_dir,
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

if platform == 'win32':
    package_data = {"monetdbe": ["*.dll"]}
else:
    package_data = {}

class build_ext(_build_ext):
    def finalize_options(self):
        _build_ext.finalize_options(self)
        opt = get_monetdbe_paths()
        if opt['include_dir'] and opt['library_dir']:
            self.include_dirs.append(opt['include_dir'])
            self.library_dirs.append(opt['library_dir'])

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
    cffi_modules=["monetdbe/_cffi/builder.py:ffibuilder"],
    cmdclass = {'build_ext': build_ext},
    install_requires=["cffi>=1.0.0", "numpy", "pandas"],
    tests_require=tests_require,
    test_suite="tests",
    package_data=package_data,
)
