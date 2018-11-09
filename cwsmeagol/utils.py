import json
import re
import urllib
import inspect
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


def missing_attribute(cls, instance, attr):
    try:
        return getattr(super(cls, instance), attr)
    except AttributeError:
        class_name = instance.__class__.__name__
        error = "{0} instance has no attribute '{1}'"
        raise AttributeError(error.format(class_name, attr))


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
    return text


def remove_text(item, text):
    return change_text(item, '', text)


def score_pattern(word, pattern, radix, points):
    return sum([points * radix**index
                for index in pattern_indices(word, pattern)])


def pattern_indices(word, pattern):
    index = -1
    while True:
        try:
            index = word.index(pattern, index + 1)
            yield index + 1
        except ValueError:
            raise StopIteration


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
