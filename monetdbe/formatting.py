from re import compile, sub, DOTALL
from string import Formatter
from typing import Dict, Optional, Union, Iterable, Any, List, Sized, Collection, Sequence, Mapping

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


parameters_type = Optional[Union[Sequence[Any], Dict[str, Any]]]


def _format_mapping(cleaned_query: str, parameters: Dict[str, Any], query: str):
    if '?' in cleaned_query:
        raise ProgrammingError("'?' in formatting with mapping as parameters")

    escaped: Dict[str, str] = {k: convert(v) for k, v in parameters.items()}

    if ':' in cleaned_query:  # qmark
        x = sub(r':(\w+)', r'{\1}', query)
    elif '%' in cleaned_query:
        return query % escaped

    if hasattr(type(parameters), '__missing__'):
        # this is something like a dict with a default value
        try:
            # mypy doesn't understand that this is a dict-like with a default __missing__ value
            return DefaultFormatter(parameters).format(x, **escaped)
        except KeyError as e:
            raise ProgrammingError(e)
    try:
        return x.format(**escaped)
    except KeyError as e:
        raise ProgrammingError(e)


def _format_iterable(cleaned_query: str, parameters: Sequence[Any], query: str):
    # we do this a bit strange to make sure the test_ExecuteParamSequence sqlite test passes
    escaped_list: List[str] = [convert(parameters[i]) for i in range(len(parameters))]

    if ':' in cleaned_query:
        x = sub(r':(\w+)', r'{\1}', query)

        # The numbering used starts at 1, while python starts 0, so we insert a bogus prefix
        prefixed = [''] + escaped_list

        return x.format(*prefixed)

    if '?' in cleaned_query:  # qmark style

        if cleaned_query.count('?') != len(escaped_list):
            raise ProgrammingError(f"Number of arguments ({len(escaped_list)}) doesn't "
                                   f"match number of '?' ({cleaned_query.count('?')})")

        return query.replace('?', '{}').format(*escaped_list)
    elif '%s' in cleaned_query:  # pyformat style
        return query % tuple(escaped_list)
    else:
        return cleaned_query


def format_query(query: str, parameters: parameters_type = None) -> str:
    if type(query) != str:
        raise TypeError

    cleaned_query = remove_quoted_substrings(query)

    if parameters is None:
        for symbol in ':?':
            if symbol in cleaned_query:
                raise ProgrammingError(f"unexpected symbol '{symbol}' in operation")
        return query

    # named, numeric or format style
    if isinstance(parameters, Dict):
        return _format_mapping(cleaned_query, parameters, query)

    # qmark or pyformat style
    elif isinstance(parameters, Sequence) or (isinstance(parameters, Sized) and hasattr(parameters, '__getitem__')):
        return _format_iterable(cleaned_query, parameters, query)

    else:
        raise ValueError(f"parameters '{parameters}' type '{type(parameters)}' not supported")


