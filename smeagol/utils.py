import os
import re
import sys
import json
import urllib.request, urllib.parse, urllib.error
import inspect
import functools
from .errors import *
from threading import Thread
from datetime import datetime
from contextlib import contextmanager
from .translation.markdown import Markdown


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
            value = function(self, *args, **kwargs)
            self.html_to_tkinter()
            return value
        return wrapper
    return decorator

def timeit(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        oldtime = datetime.now()
        value = function(*args, **kwargs)
        newtime = datetime.now()
        print(('Done: ' + str(newtime - oldtime)))
        return value
    return wrapper

def asynca(function):
    @functools.wraps(function)
    def async_function(*args, **kwargs):
        thread = Thread(target=function, args=args, kwargs=kwargs)
        thread.start()
        return thread
    return async_function

def dump(dictionary, filename):
    if filename:
        with ignored(os.error):
            os.makedirs(os.path.dirname(filename))
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(dictionary, f, indent=4)


def dumps(string, filename):
    if filename:
        with ignored(os.error):
            os.makedirs(os.path.dirname(filename))
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(string)


def buyCaps(word):
    return re.sub(r'[$](.)', _buy, word).replace('.', '&nbsp;')


def _buy(regex):
    return regex.group(1).capitalize()


def sellCaps(word):
    return re.sub(r'(.)', _sell, word.replace(' ', '.'))

def _sell(regex):
    letter = regex.group(1)
    if letter != letter.lower():
        return '$' + letter.lower()
    else:
        return letter

def is_key(text):
    return not re.match('^[A-Z].+', text)

def change_text(item, replacement, text):
    try:
        text[0] = re.sub(item, replacement, text[0])
    except FutureWarning:
        print(item)
    return text

def remove_text(item, text):
    return change_text(item, '', text)

own_markdown = Markdown()

def un_url(text, markdown=None):
    try:
        markup = markdown.to_markup
    except AttributeError:
        markup = own_markdown.to_markup
    text = text.replace(' ', '.')
    return sellCaps(markup(text))

def urlform(text):
    name = text.lower()
    # remove tags, text within tags, and spaces
    name = re.sub(r'(<(div|ipa).*?\2>)|<.*?>| ', '', name)
    return name

def page_initial(text):
    '''Returns the first letter of a word, i.e.: the folder of the Dictionary
        in which that word would appear
        @error: IndexError if the text only contains punctuation'''
    name = own_markdown.to_markdown(text)
    name = re.sub("'", '', name)
    return re.findall(r'\w', name)[0]

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

    def __next__(self):
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
