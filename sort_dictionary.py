import re
import random

from smeagol.utilities import filesystem as fs


def sortkey(elt):
    return re.sub(r'\W', '', elt[0])


text = fs.load_yaml(
    'c:/users/ryan/tinellbianlanguages/dictionary/data/data.src')
lex = text['entries']['children']['The Tinellbian Languages Dictionary']['children']['lex']['children']
lex = dict(sorted(lex.items(), key=lambda x: x[0]))
lex = dict(sorted(lex.items(), key=sortkey))
text['entries']['children']['The Tinellbian Languages Dictionary']['children']['lex']['children'] = lex
fs.save_yaml(text, 'c:/users/ryan/onedrive/desktop/sorting.yml')
