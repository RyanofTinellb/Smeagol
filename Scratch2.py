import cProfile
import random
from Smeagol import *

grammar = Grammar()
for item in grammar:
    print(item.hyperlink(grammar.root))
