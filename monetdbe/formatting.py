from re import compile, sub, DOTALL
from string import Formatter
from typing import Dict, Optional, Union, Iterable, Any

from monetdbe.exceptions import ProgrammingError

# use this pattern to split a string on non-escaped semicolumns
semicolumn_split_pattern = compile(r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')


def strip_split_and_clean(script: str):
    """
    This will split the query on unescaped semicolumns, cleanup every subquery from comments and remove any
    empty queries from the result.

    args:
        script: one ore more SQL queries split by a semicolum
    """

    results = []
    for q in semicolumn_split_pattern.split(script)[1::2]:
        q = sub('^\s*--.*\n?', '', q)
        q = sub(r'/*.*\*/', '', q, flags=DOTALL)
        q = q.strip()
        if q:
            results.append(q)

    return results


def escape(v):
    return f"'{v}'"


class DefaultFormatter(Formatter):
    """
    This makes it possible to supply a dict with a __missing__() method (like a defaultdict)
    """

    def __init__(self, d: Dict):
        super().__init__()
        self.d = d

    def get_value(self, key, *args, **kwargs):
        s = self.d[key]
        if isinstance(s, str):
            return escape(s)
        else:
            return s


def format_query(query: str, parameters: Optional[Union[Iterable[str], Dict[str, Any]]] = None) -> str:
    if type(query) != str:
        raise TypeError

    if parameters is not None:
        if hasattr(type(parameters), '__getitem__') and hasattr(type(parameters), 'keys'):  # qmark style

            if '?' in query:
                raise ProgrammingError("'?' in formatting with qmark style parameters")

            # we ignore type below, since we already check if there is a keys method, but mypy doesn't undertand
            escaped = dict((k, escape(v)) if type(v) == str else (k, v) for k, v in parameters.items())  # type: ignore
            x = sub(r':(\w+)', r'{\1}', query)

            if hasattr(type(parameters), '__missing__'):
                # this is something like a dict with a default value
                try:
                    # mypy doesn't understand that this is a dict-like with a default __missing__ value
                    return DefaultFormatter(parameters).format(x, **escaped)  # type: ignore
                except KeyError as e:
                    raise ProgrammingError(e)
            try:
                return x.format(**escaped)
            except KeyError as e:
                raise ProgrammingError(e)
        elif hasattr(type(parameters), '__iter__'):  # named style

            if ':' in query:
                raise ProgrammingError("':' in formatting with named style parameters")

            # mypy gets confused here
            escaped = [f"'{i}'" if type(i) == str else i for i in parameters]  # type: ignore
            return query.replace('?', '{}').format(*escaped)
        else:
            raise ValueError(f"parameters '{parameters}' type '{type(parameters)}' not supported")
    else:
        # TODO: (gijs) this should probably be a bit more elaborate, support for escaping for example
        for symbol in ':?':
            if symbol in query:
                raise ProgrammingError(f"unexpected symbol '{symbol}' in operation")
        return query
