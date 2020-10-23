from setuptools import find_packages, setup
from sys import platform

with open("README.md", "r") as fh:
    long_description = fh.read()

tests_require = ['pytest', 'mypy', 'pycodestyle', 'data-science-types']

extras_require = {
    'test': tests_require,
    'doc': ['sphinx', 'sphinx_rtd_theme'],

}

packages = find_packages(exclude=['tests', 'tests.test_lite'])

if platform == 'win32':
    package_data = {"monetdbe": ["*.dll"]}
else:
    package_data = {}


setup(
    name="monetdbe",
    version="0.9",
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
    python_requires='>=3.6',
    setup_requires=["cffi>=1.0.0"],
    extras_require=extras_require,
    cffi_modules=["monetdbe/_cffi/builder.py:ffibuilder"],
    install_requires=["cffi>=1.0.0", "numpy", "pandas"],
    tests_require=tests_require,
    test_suite="tests",
    package_data=package_data,
)
