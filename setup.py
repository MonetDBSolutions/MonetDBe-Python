import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

tests_require = ['pytest', 'mypy', 'pycodestyle']

extras_require = {
    'test': tests_require,
    'doc': ['sphinx', 'sphinx_rtd_theme'],

}

setuptools.setup(
    name="monetdbe",
    version="0.8.2",
    author="Gijs Molenaar",
    author_email="gijs@pythonic.nl",
    description="MonetDBe - the Python embedded MonetDB",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/monetdBSolutions/MonetDBe-Python/",
    packages=setuptools.find_packages(),
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
    cffi_modules=["monetdbe/util/builder.py:ffibuilder"],
    install_requires=["cffi>=1.0.0", "numpy", "pandas"],
    tests_require=tests_require,
    test_suite="tests",
)
