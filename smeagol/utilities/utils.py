import functools
from itertools import cycle
import os
import re
import tkinter as tk
from contextlib import contextmanager
from datetime import datetime as dt
from threading import Thread
from typing import Any


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


def apply_functions_alternately(functions: list, obj: Any):
    for f, x in zip(cycle(functions), obj):
        f(x)


def setnonzero(obj, attr, value):
    if not value:
        return obj.pop(attr, None)
    obj[attr] = value


def setnotequal(obj, attr, value, default):
    if value == default:
        return obj.pop(attr, None)
    obj[attr] = value


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


def stringify(obj, indent=0):
    output = ""
    if isinstance(obj, dict):
        for k, v in obj.items():
            output += f'{indent * "-"}{k} - {stringify(v, indent+2)}'
    elif isinstance(obj, list) or isinstance(obj, tuple):
        for v in obj:
            output += f'{indent * "-"}{stringify(v, indent+2)}'
    else:
        output += f'{indent * "-"}{obj}'
    return output


def buyCaps(word):
    return re.sub(r"[$](.)", _buy, word).replace(".", "&nbsp;")


def _buy(regex):
    return regex.group(1).capitalize()


def sellCaps(word):
    return re.sub(r"(.)", _sell, word.replace(" ", "."))


def _sell(regex):
    letter = regex.group(1)
    if letter != letter.lower():
        return "$" + letter.lower()
    else:
        return letter


def change_text(item, replacement, text):
    try:
        text[0] = re.sub(item, replacement, text[0])
    except FutureWarning:
        print(item)
    return text


tk.FIRST = 0
tk.LAST = tk.END
tk.ALL = (tk.FIRST, tk.LAST)


def Tk_compare(tb, first, op, second):
    try:
        return tb.compare(first, op, second)
    except tk.TclError:
        return tb.compare(tk.INSERT, op, second)


def remove_text(item, text):
    return change_text(item, "", text)


def un_url(text, markdown=None):
    text = text.replace(" ", ".")
    if markdown:
        text = markdown.to_markup(text)
    return sellCaps(text)


def urlform(text):
    name = text.lower()
    # remove tags, text within tags, and spaces
    name = re.sub(r"(<(div|ipa).*?\2>)|<.*?>| ", "", name)
    return name


def page_initial(name, markdown=None):
    """Returns the first letter of a word, i.e.: the folder of the Dictionary
    in which that word would appear
    @error: IndexError if the text only contains punctuation"""
    if markdown:
        name = markdown.to_markdown(name)
    return re.findall(r"\w", name)[0]


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
