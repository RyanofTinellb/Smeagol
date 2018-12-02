import os
import re
import sys
import json
import urllib
import inspect
import functools
from contextlib import contextmanager
from datetime import datetime
from translation.markdown import Markdown


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass

def tkinter():
    def decorator(function):
        @functools.wraps(function)
        def wrapper(self, *args, **kwargs):
            self.tkinter_to_html()
            function(self, *args, **kwargs)
            self.html_to_tkinter()
        return wrapper
    return decorator


def dump(dictionary, filename):
    if filename:
        with ignored(os.error):
            os.makedirs(os.path.dirname(filename))
        with open(filename, 'w') as f:
            json.dump(dictionary, f, indent=4)


def dumps(string, filename):
    if filename:
        with ignored(os.error):
            os.makedirs(os.path.dirname(filename))
        with open(filename, 'w') as f:
            f.write(string)


def buyCaps(word):
    return re.sub(r'[$](.)', _buy, word)


def _buy(regex):
    return regex.group(1).capitalize()


def sellCaps(word):
    return re.sub(r'([A-Z])', _sell, word)


def _sell(regex):
    return '$' + regex.group(1).lower()


def change_text(item, replacement, text):
    text[0] = re.sub(item, replacement, text[0])
    return text


def remove_text(item, text):
    return change_text(item, '', text)


def urlform(text, markdown=None):
    try:
        markdown = markdown.to_markdown
    except AttributeError:
        markdown = Markdown().to_markdown
    name = [text.lower()]
    safe_punctuation = '\'._+!(),'
    # remove safe punctuations that should only be used to encode non-ascii characters
    remove_text(r'[{0}]'.format(safe_punctuation), name)
    name[0] = markdown(name[0])
    # remove extraneous initial apostrophes
    change_text(r"^''+", "'", name)
    # remove text within tags
    remove_text(r'<(div|ipa).*?\1>', name)
    # remove tags, spaces and punctuation
    remove_text(r'<.*?>|[/*;: ]', name)
    name = urllib.quote(name[0], safe_punctuation + '$')
    return name


class ShortList(list):
    def __init__(self, arr, max_length):
        if len(arr) > max_length:
            arr = arr[:max_length]
        super(ShortList, self).__init__(arr)
        self.max_length = max_length

    def __iadd__(self, other):
        self.append(other)
        if len(self) > self.max_length:
            self.pop(0)
        return self

    def replace(self, other):
        try:
            self[-1] = other
        except IndexError:
            self += other
        return self

    def next(self):
        try:
            page = self.pop(0)
        except IndexError:
            return None
        self += page
        return page

    def previous(self):
        try:
            self.insert(0, self.pop())
        except IndexError:
            return None
        return self[-1]
