import functools
import inspect
import json
import os
import re
import sys
import tkinter as Tk
import tkinter.messagebox as mb
import tkinter.simpledialog as sd
import tkinter.filedialog as fd
import urllib.error
import urllib.parse
import urllib.request
from contextlib import contextmanager
from datetime import datetime as dt
from threading import Thread

from .errors import *
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
        oldtime = dt.now()
        value = function(*args, **kwargs)
        newtime = dt.now()
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
            json.dump(dictionary, f, ensure_ascii=False, indent=4)


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


def change_text(item, replacement, text):
    try:
        text[0] = re.sub(item, replacement, text[0])
    except FutureWarning:
        print(item)
    return text

Tk.START = '1.0'
Tk.FIRST = 0
Tk.FINAL = Tk.END
Tk.END = Tk.END + '-1c'
Tk.LINESTART = Tk.INSERT + ' linestart'
Tk.LINEEND = Tk.INSERT + ' lineend+1c'
Tk.CURRLINE = (Tk.LINESTART, Tk.LINEEND)
Tk.PREV_LINE = Tk.INSERT + ' linestart -1l'
Tk.NEXT_LINE = Tk.INSERT + ' linestart +1l'
Tk.SELECTION = (Tk.SEL_FIRST, Tk.SEL_LAST)
Tk.SEL_LINE = (Tk.SEL_FIRST + ' linestart', Tk.SEL_LAST + ' lineend+1c')
Tk.NO_SELECTION = (Tk.INSERT,) * 2
Tk.USER_MARK = 'usermark'
Tk.WHOLE_BOX = (Tk.START, Tk.END)
Tk.WHOLE_ENTRY = (Tk.FIRST, Tk.FINAL)

def Tk_compare(tb, first, op, second):
    try:
        return tb.compare(first, op, second)
    except Tk.TclError:
        return tb.compare(Tk.INSERT, op, second)

BRACKETS = {'[': ']', '<': '>', '{': '}', '"': '"', '(': ')'}

def move_mark(textbox, mark, size):
    sign = '+' if size >= 0 else '-'
    size = abs(size)
    textbox.mark_set(Tk.INSERT, mark)
    textbox.mark_set(mark, f'{mark}{sign}{size}c')

def remove_text(item, text):
    return change_text(item, '', text)

def get_text(textbox):
    return textbox.get(*Tk.WHOLE_BOX)

def get_formatted_text(textbox):
    return textbox.dump(*Tk.WHOLE_BOX)

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

class Text:
    def __init__(self, master, text=''):
        with ignored(AttributeError):
            text = ''.join(map(self.add_tags, get_formatted_text(text)))
        self.text = text
        self.entry = master.entry
        self.master = master

    def __getattr__(self, attr):
        if attr.endswith('_links'):
            self.text = getattr(self.master, attr)(self.text, self.entry)
            return self
        elif attr.startswith('mark'):
            self.text = getattr(self.master, attr)(self.text)
            return self
        else:
            return getattr(super(), attr)
        
    def __str__(self):
        return self.text
    
    def add_tags(self, tag):
        key, value, index = tag
        if key == 'tagon':
            if value.startswith('example'):
                return '['
            elif value in (Tk.SEL, ''):
                return ''
            else:
                return f'<{value}>'
        elif key == 'text':
            return value
        elif key == 'tagoff':
            if value.startswith('example'):
                return ']'
            elif value in (Tk.SEL, ''):
                return ''
            else:
                return f'</{value}>'
        return ''
