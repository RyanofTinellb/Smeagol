from smeagol.utilities import filesystem as fs
import random

filename = 'c:/users/ryan/tinellbianlanguages/dictionary/data/assets/wordlist.json'

def custFil(elt):
    # return elt['l'] d == 'High Lulani' and elt['t'].endswith('ira')
    return elt['l'] == 'High Lulani' and 'derived' not in elt['p'] and 'proper' not in elt['p'] and len(elt['t'].replace('-', '')) > 5 and ' ' not in elt['t']

text = fs.load_json(filename)
text = list(filter(custFil, text))
# print('\n'.join(elt['t'] for elt in text))
choice = random.choice(text)
print('1/' + str(len(text)) + ': ' + choice['t'] + ' - ' + choice['d'].split(';')[0])