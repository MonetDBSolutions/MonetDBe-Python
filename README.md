# MonetDB/e-Python

MonetDB/e-Python - the serverless Python embedded MonetDB

![alt text](monetdbe-python.png)

Want to store and search a massive amount of numbers? You don't want to run a database service? Is SQLite too slow for what you want to do? Search no further! MonetDBe-Python is here. Just pip install the binary wheel on your Windows, Linux or OS X system and you are ready to go, no compilation needed.

MonetDBe-Python internally relies on a serverless and trimmed-down version of the blazingly fast MonetDB, the open-source column-store database.

The documentation can be found at: https://monetdbe.readthedocs.io/

The source code can be found at: https://github.com/monetdBSolutions/MonetDBe-Python/


# install

you need:

 * An up-to-date Linux, OSX or Windows 
 * pip `>= 19.3`
 * Python `>= 3.6`

to make sure you have a recent pip first upgrade pip:
```
$ pip install --upgrade pip
```

now you can install MonetDBe-Python with:
```
$ pip install monetdbe
```


# usage

Just import and get started, no running a server required. Connecting without
an argument starts an in-memory storage instance:
```
>>> from monetdbe import connect
>>> con = connect()
>>> con.execute('select * from tables').fetchdf()
      id               name  schema_id                                              query  type  system  commit_action  access  temporary
0   2001            schemas       2000                                               None    10    True              0       0          0
1   2007              types       2000                                               None    10    True              0       0          0
2   2016          functions       2000                                               None    10    True              0       0          0
3   2029               args       2000                                               None    10    True              0       0          0
4   2038          sequences       2000                                               None    10    True              0       0          0
..   ...                ...        ...                                                ...   ...     ...            ...     ...        ...
81  6650       storagemodel       2000  create view sys.storagemodel as\nselect "schem...    11    True              0       0          0
82  6661  tablestoragemodel       2000  create view sys.tablestoragemodel as\nselect "...    11    True              0       0          0
83  6675         statistics       2000                                               None    10    True              0       0          0
84  6734           compinfo       6698  create view logging.compinfo as select * from ...    11    True              0       0          0
85  6739    systemfunctions       2000  create view sys.systemfunctions as select id a...    11    True              0       0          0
```

See a another simple example illustrating the Pandas support in this notebook:

https://github.com/MonetDBSolutions/MonetDBe-Python/blob/master/notebooks/basic_example.ipynb

