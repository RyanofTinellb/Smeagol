from smeagol.utilities import filesystem as fs
import random

filename = 'c:/users/ryan/tinellbianlanguages/dictionary/data/assets/wordlist.json'

def custFil(elt):
    return elt['l'] == 'High Lulani' and 'derived' not in elt['p'] and len(elt['t']) > 5

text = fs.load_json(filename)
text = list(filter(custFil, text))
print('1/' + str(len(text)) + ': ' + random.choice(text)['t'])