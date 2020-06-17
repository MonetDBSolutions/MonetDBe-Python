from re import compile, sub, DOTALL
from string import Formatter
from typing import Dict, Optional, Union, Iterable, Any, List, Sized

from monetdbe.exceptions import ProgrammingError
from monetdbe.monetize import convert

# use this pattern to split a string on non-escaped semicolumns
semicolumn_split_pattern = compile(r'''((?:[^;"']|"[^"]*"|'[^']*')+)''')


def remove_quoted_substrings(query: str):
    """
    This removes all quoted substrings. Note that this likely results in a broken query.
    """
    q = sub(r"\\'", "", query)  # first remove escaped quotes
    q = sub(r"'(.*)'", "", q)  # then remove all quotes strings
    return q


def strip_split_and_clean(script: str):
    """
    This will split the query on unescaped semicolumns, cleanup every subquery from comments and remove any
    empty queries from the result.

    args:
        script: one ore more SQL queries split by a semicolum
    """

    results = []
    for q in semicolumn_split_pattern.split(script)[1::2]:
        q = sub(r'^\s*--.*\n?', '', q)
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


# todo (gijs): check typing
def format_query(query: str,  # type: ignore
                 parameters: Optional[Union[Iterable[str], Dict[str, Any], Sized]] = None) -> str:  # type: ignore
    if type(query) != str:
        raise TypeError

    cleaned_query = remove_quoted_substrings(query)

    if parameters is not None:
        # named, numeric or format style
        if hasattr(type(parameters), '__getitem__') and hasattr(type(parameters), 'keys') \
                and hasattr(type(parameters), 'items'):

            if '?' in cleaned_query:
                raise ProgrammingError("'?' in formatting with mapping as parameters")

            escaped: Dict[str, str] = {k: convert(v) for k, v in parameters.items()}  # type: ignore

            if ':' in cleaned_query:  # qmark
                x = sub(r':(\w+)', r'{\1}', query)
            elif '%' in cleaned_query:  # pyformat
                return query % escaped

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

        # qmark or pyformat style
        elif hasattr(type(parameters), '__iter__') \
                or (hasattr(type(parameters), '__len__') and hasattr(type(parameters), '__getitem__')):

            # todo (gijs): check typing
            # we do this a bit strange to make sure the test_ExecuteParamSequence sqlite test passes
            escaped_list: List[Optional[str]] = [convert(parameters[i]) for i in range(len(parameters))]  # type: ignore

            if ':' in cleaned_query:
                # raise ProgrammingError("':' in formatting with named style parameters")
                x = sub(r':(\w+)', r'{\1}', query)

                # off by one error
                # todo (gijs): check typing
                prefixed = [None] + escaped_list  # type: ignore

                return x.format(*prefixed)

            if '?' in cleaned_query:  # named style

                if cleaned_query.count('?') != len(escaped_list):
                    raise ProgrammingError(f"Number of arguments ({len(escaped_list)}) doesn't "
                                           f"match number of '?' ({cleaned_query.count('?')})")

                return query.replace('?', '{}').format(*escaped_list)
            elif '%s' in cleaned_query:  # pyformat style
                return query % tuple(escaped_list)
        else:
            raise ValueError(f"parameters '{parameters}' type '{type(parameters)}' not supported")
    else:
        for symbol in ':?':
            if symbol in cleaned_query:
                raise ProgrammingError(f"unexpected symbol '{symbol}' in operation")
        return query
