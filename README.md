# monetdbe
MonetDBe - the Python embedded MonetDB

https://github.com/monetdBSolutions/MonetDBe-Python/

# install

```
 CFLAGS="-I<monetdb_prefix>/include/monetdb -I<monetdb_prefix>/lib/monetdb" pip install .
```
 
 
# development

![Python package](https://github.com/monetdBSolutions/MonetDBe-Python//workflows/Python%20package/badge.svg)


CFLAGS="-I$prefix/include" LDFLAGS="-L$prefix/lib64" venv/bin/pip install -e .
venv/bin/pip install pytest
venv/bin/pytest

# simple test 
venv/bin/python -c "import monetdbe; monetdbe.connect()" 
