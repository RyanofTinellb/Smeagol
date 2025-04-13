import functools
import itertools
import os
import re
import tkinter as tk
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime as dt
from threading import Thread
from typing import Iterable, Optional


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass


def timeit(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        oldtime = dt.now()
        value = function(*args, **kwargs)
        newtime = dt.now()
        print(("Done: " + str(newtime - oldtime)))
        return value
    return wrapper


def asynca(function):
    @functools.wraps(function)
    def async_function(*args, **kwargs):
        thread = Thread(target=function, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return async_function


def compose(*functions):
    def compose2(f, g):
        return lambda x: f(g(x))
    return functools.reduce(compose2, functions, lambda x: x)


def clamp(number, lower, upper):
    return max(lower, min(upper, number))


def url_form(text):
    return text.lower().replace(' ', '')


def alternate(functions: Iterable, obj: Iterable):
    for f, x in zip(itertools.cycle(functions), obj):
        f(x)


def alternate_yield(functions: Iterable, obj: Iterable, *args, **kwargs):
    for f, x in zip(itertools.cycle(functions), obj):
        yield f(x, *args, **kwargs)


def setnonzero(obj, attr, value):
    if not value:
        return obj.pop(attr, None)
    obj[attr] = value
    return None


def filter_nonzero(obj):
    return dict(filter(lambda k: k[1], obj.items()))


def setnotequal(obj, attr, value, default):
    if value == default:
        return obj.pop(attr, None)
    obj[attr] = value
    return None


def display_attrs(obj):
    for attr in dir(obj):
        value = getattr(obj, attr)
        print(attr, type(value), value)
        print()


def clear_screen():
    os.system("cls")


def increment(lst, by):
    lst = [x + by for x in lst]
    return lst


def recurse(obj, names):
    for name in names:
        obj = obj[name]
    return obj


def link(page):
    fragment = ''
    with ignored(AttributeError):
        page = page.link
    with ignored(AttributeError):
        page, fragment = try_split(page, '#')
        page = page.split('/')
    hash_ = '#' if fragment else ''
    page[-1], ext = try_split(page[-1], '.', 'html')
    open_slash = '' if page[0].startswith('http') else '/'
    return open_slash + '/'.join(page) + '.' + ext + hash_ + fragment


def groupby(obj, fn):
    obj = sorted(obj, key=fn)
    return itertools.groupby(obj, fn)


def stringify(obj, indent=0):
    output = ""
    if isinstance(obj, dict):
        for k, v in obj.items():
            output += f'{indent * "-"}{k} - {stringify(v, indent+2)}'
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            output += f'{indent * "-"}{stringify(v, indent+2)}'
    else:
        output += f'{indent * "-"}{obj}'
    return output


def change_text(item, replacement, text):
    try:
        text[0] = re.sub(item, replacement, text[0])
    except FutureWarning:
        print(item)
    return text


tk.FIRST = 0
tk.LAST = tk.END
tk.ALL = (tk.FIRST, tk.LAST)


def try_split(string, sep=None, default='', maxsplit=1):
    with ignored(ValueError):
        string, default = string.split(sep, maxsplit)
    return string, default


def remove_text(item, text):
    return change_text(item, "", text)


def remove_common_prefix(*lists):
    uniques = [len(set(elts)) for elts in zip(*lists)]
    try:
        index = next(i for i, item in enumerate(uniques) if item > 1)
    except StopIteration:
        index = min((len(lst) for lst in lists))
    for lst in lists:
        del lst[:index]


def buy_caps(text):
    return re.sub(r'\$(.)', lambda match: match.group(1).upper(), text.replace('.', ' '))


def sell_caps(text):
    return ''.join(letter if letter.lower() == letter else f'${letter.lower()}' for letter in text)


def bind_all(obj, commands):
    for command in commands:
        obj.bind(*command)


def reorder(lst, obj):
    """reorder a dictionary's key based on a given list"""
    if isinstance(obj, list):
        for o in obj:
            reorder(lst, o)
    elif isinstance(obj, dict):
        for v in obj.values():
            reorder(lst, v)
        for itm in lst:
            with ignored(KeyError):
                t = obj.pop(itm)
                obj[itm] = t


def default_title(entry):
    root = entry.root.name
    match root:
        case 'A Grammar of the Tinellbian Languages':
            return _grammar_title(entry, root)
        case _default:
            return f'{entry.name} - {root}'


def _grammar_title(entry, root):
    match entry.level:
        case 0:
            return root
        case 1 | 2:
            name = entry.name
        case 3:
            name = _language_name(entry)
        case _other:
            name = f'{_language_name(entry)} {entry.name}'
    return f'{name} - {root}'


def _language_name(entry):
    language = ' '.join(reversed(entry.names[2:4]))
    return language.replace('Proto ', 'Proto-')


class DateFormatter:
    def __init__(self, date, str_format):
        self.date = date
        self.str_format = str_format
        self.in_string = False
        self.formats = {
            'dd': '%d', 'ddd': '%a', 'dddd': '%A',
            'mm': '%m', 'mmm': '%B', 'mmmm': '%B',
            'yy': '%y', 'yyy': '%Y', 'yyyy': '%Y'
        }

    def __str__(self):
        tokens = re.split(r'(\W)', self.str_format)
        return ''.join((self._format_date(token) for token in tokens))

    def ordinal_suffix(self, n):
        return ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)] if n // 10 != 1 else 'th'

    def _format_date(self, token):
        if token == '"':
            self.in_string = not self.in_string
            return ''
        if self.in_string:
            return token
        ord_suffix = token and token.endswith('r')
        match token.removesuffix('r'):
            case 'd':
                value = self.date.day
            case 'm':
                value = self.date.month
            case 'y':
                value = self.date.year
            case key:
                try:
                    value = self.date.strftime(self.formats[key])
                except KeyError:
                    return key
        suffix = self.ordinal_suffix(value) if ord_suffix else ''
        return f'{value}{suffix}'


def format_date(date, str_format):
    return str(DateFormatter(date, str_format))


@dataclass
class Clipboard:
    text: str = ''
    compare: str = ''


@dataclass
class Flag:
    tag: Optional[str] = ''

    def __bool__(self):
        return bool(self.tag)

    def update(self, tag=''):
        self.tag = tag
