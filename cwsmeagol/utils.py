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
    try:
        yield getattr(converter, function)
    except AttributeError:
        yield lambda x: x
    # except:
    #     raise

def dump(dictionary, filename):
    if filename:
        with open(filename, 'w') as f:
            json.dump(dictionary, f, indent=2)

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

def remove_text(item, text):
    change_text(item, '', text)

url_markdown = Markdown()

def urlform(text, markdown=None):
    markdown = markdown or url_markdown
    name = [text.lower()]
    safe_punctuation = '\'._+!(),'
    # remove safe punctuations that should only be used to encode non-ascii characters
    remove_text(r'[{0}]'.format(safe_punctuation), name)
    with conversion(markdown, 'to_markdown') as converter:
        name[0] = converter(name[0])
    # remove extraneous initial apostrophes
    change_text(r"^''+", "'", name)
    # remove text within tags
    remove_text(r'<(div|ipa).*?\1>', name)
    # remove tags, spaces and punctuation
    remove_text(r'<.*?>|[/*;: ]', name)
    name = urllib.quote(name[0], safe_punctuation + '$')
    return name

def add_datestamp(text):
    text += datetime.strftime(datetime.today(), '&date=%Y%m%d')
    return text

def remove_datestamp(text):
    return re.sub(r'&date=\d{8}', '', text)

def replace_datestamp(text):
    return add_datestamp(remove_datestamp(text))
