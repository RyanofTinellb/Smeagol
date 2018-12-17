from smeagol.translation.evolve import HighToColloquialLulani
import json
import re
import os
import webbrowser as web

def unique(lst):
    return [lst[0]] + [y for x,y in zip(lst, lst[1:]) if x != y]

class Verbs:
    def __init__(self, file):
        self.file = file

    def markdown(self, word):
        return word.replace(
        '&rsquo;', "'").replace('&middot;', 'o').replace('&#x294;', "''")

    def markup(self, word):
        return word.replace(
            "''", '&#x294;').replace('o', '&middot;').replace("'", '&rsquo;')

    def passive(self, word):
        word = self.markdown(word)
        if re.search(r'^[pbtdcjkgmnqlrfsxh\'][aiuo]$', word):
            word += "'illu"
        elif re.search(r'([pbtdcjkgmnqlrfsxh\'])\1[aiuo]$', word):
            word = word[:-1] + 'ilu'
        else:
            word = word[:-1] + 'illu'
        return self.markup(word)

    def ablative(self, word):
        word = self.markdown(word)
        if re.search(r'([pbtdcjkgmnqlrfsxh\'])\1[aiuo]$', word):
            word += 'ka'
        else:
            word += 'kka'
        return self.markup(word)

    def dative(self, word):
        return word + 'xa'

    @property
    def conjugation(self):
        colloquial = HighToColloquialLulani()
        output = json.load(self.file)
        verbs = [entry['t'] for entry in output if 'verb' in entry['p'] and
            entry['l'] == 'High Lulani']
        verbs.sort(key=lexi_sort)
        auxes = ['', 'qixa', 'rusa', 'cani', 'nagi', 'funi',
                'lanu',  'qilu', 'taku', 'ruku',
                'hu',  'na', 'ji', 'pi', 'ru', "ra&rsquo;u",
            ]
        output = []
        for verb in verbs:
            for aux in auxes:
                y = verb
                output += [verb + aux]
        return unique([colloquial.evolve(x) for x in output])

def lexi_sort(word):
    last_vowel = word[-1]
    hyphen = '-' in word
    syll_number = len(re.findall(r'[aiu]', word))
    return hyphen, last_vowel, syll_number

def lexicon(file):
    return unique([HighToColloquialLulani().evolve(entry['t'].lower())
        for entry in json.load(file) if entry['l'] == 'High Lulani'])

def sandhi_check():
    consonants = 'pbtdcjkgmnqlrfsxh'
    return [HighToColloquialLulani().evolve(x) for y in [
        [string.format(a, b) for string in [
            '{0}a{1}a&rsquo;a', '&rsquo;a{0}a{1}a&rsquo;a', '&rsquo;a{0}{0}a{1}a']
        ]
        for a in consonants for b in consonants]
            for x in y]

os.chdir('c:/users/ryan/documents/tinellbianlanguages/dictionary')
print '''1. Verbs conjugation
2. Sandhi check
3. Normal lexicon
4. Exit'''
option = raw_input('Choice: ')
if option == '1':
    with open('wordlist.json') as f:
        wordlist = Verbs(f).conjugation
    with open('colloquialverbs.json', 'w') as f:
        json.dump(wordlist, f, indent=2)
    web.open('colloquialverbs.html')
elif option == '2':
    wordlist = sandhi_check()
    with open('colloquiallulani.json', 'w') as f:
        json.dump(wordlist, f, indent=2)
    web.open('colloquiallulani.html')
elif option == '3':
    with open('wordlist.json') as f:
        wordlist = lexicon(f)
    with open('colloquiallulani.json', 'w') as f:
        json.dump(wordlist, f, indent=2)
    web.open('colloquiallulani.html')
