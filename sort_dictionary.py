import re
import random

from smeagol.utilities import filesystem as fs
from smeagol.utilities.tinellbian_sort import SerialNumberer

filename = 'c:/users/ryan/tinellbianlanguages/dictionary/data/data.src'
text = fs.load_yaml(filename)
lex = text['entries']['children']['The Tinellbian Languages Dictionary']['children']['lex']['children']
lex = dict(sorted(lex.items(), key=lambda x: [s.change(n) for n in x.split('.')]))
text['entries']['children']['The Tinellbian Languages Dictionary']['children']['lex']['children'] = lex
fs.save_yaml(text, filename)
