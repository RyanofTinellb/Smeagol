import json
import re
import urllib
from contextlib import contextmanager
from datetime import datetime
from translation.markdown import Markdown

@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass

@contextmanager
def conversion(converter, function):
    """
    Ensures a converter exists.
    Returns identity function if not.
    :param converter (object):
    :param function (str):
    """
    try:
        yield getattr(converter, function)
    except AttributeError:
        yield lambda x: x

url_markdown = Markdown()

def urlform(text, markdown=None):
    markdown = markdown or url_markdown
    name = text.lower()
    safe_punctuation = '\'.$_+!(),'
    # remove safe punctuations that should only be used to encode non-ascii characters
    name = re.sub(r'[{0}]'.format(safe_punctuation), '', name)
    with conversion(markdown, 'to_markdown') as converter:
        name = converter(name)
    # remove extraneous initial apostrophes
    name = re.sub(r"^''+", "'", name)
    # remove text within tags
    name = re.sub(r'<(div|ipa).*?\1>', '', name)
    # remove tags, spaces and punctuation
    name = re.sub(r'<.*?>|[/*;: ]', '', name)
    name = urllib.quote(name, safe_punctuation)
    return name

def add_datestamp(text):
    text += datetime.strftime(datetime.today(), '&date=%Y%m%d')
    return text

def remove_datestamp(text):
    return re.sub(r'&date=\d{8}', '', text)

def replace_datestamp(text):
    return add_datestamp(remove_datestamp(text))

def unique(lst):
    return [lst[0]] + [y for x,y in zip(lst, lst[1:]) if x != y]
