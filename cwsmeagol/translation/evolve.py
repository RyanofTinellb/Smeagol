import re
import json
from random import shuffle

class regexString:
    def __init__(self, string):
        self.string = string

    def remove(self, regex):
        self.string = self.sub(regex, '')
        return self

    def sub(self, pattern, sub, show=True):
        self.string = ' '.join(
                    map(lambda string: re.sub(pattern, sub, string),
                        self.string.split(' ')))
        return self

    def __str__(self):
        return re.sub(r'\d', '', self.string)
        return self.string


def evolve(text):
    text = regexString(text)
    rewrites = [
        ('&rsquo;', "'"),
        ('&middot;', '.'),
        ('&#x294;', '"'),
        ('&eth;', 'D'),
        ('&uuml;', 'U'),
        ('&ntilde;', 'N'),
        ('&#x6c;&#x303;', 'L'),
        ('&ccedil;', 'H'),
        ('&#x17e;', 'Z'),
        ('&#x2c8;', '1'),
        ('&#x2cc;', '2'),
    ]
    for rewrite in rewrites:
        text.sub(*rewrite)
    output = [str(text)]
    for rewrite in rewrites[::-1]:
        output[0] = output[0].replace(*rewrite[::-1])
    batches = [
        [('nn', 'NN'),
        ('ll', 'LL'),
        ("''", "yy"),
        ("hh", "HH")],
        # frication of geminate voiced plosives, and
        # voicing of geminate voiceless plosives
        [(r'bb', r'vv'),
        (r'dd', r'DD'),
        (r'gg', r'rr'),
        (r'pp', r'bb'),
        (r'tt', r'dd'),
        (r'cc', r'jj'),
        (r'kk', r'gg')],
        # umlaut
        [(r'a(?=.{1,2}i)', 'e'),
        (r'u(?=.{1,2}i)', 'U')],
        # replacement of glottal stop
        [(r'a\'e', r'aye')],
        # palatalisation of segments before /i/
        [(r's(?=i|si)', 'x'),
        (r't(?=i|ti)', 'c'),
        (r'd(?=i|di)', 'j'),
        (r'n(?=i|ni)', 'N'),
        (r'l(?=i|li)', 'L')],
        # stress markers
        [(r'((\w)\2)', r'\g<1>2'),
        (r'([aiueU.][pbtdDcjkg\'mnqrlfsxhNLHy])([aiueU.])$', r'\g<1>2\2'),
        (r'([pbtdDcjkg\'mnqrlfsxhNLHy][aiueU.][pbtdDcjkg\'mnqrlfsxhNLHy]+2)', r'1\1'),
        (r'([aiueU.][pbtdDcjkg\'mnqrlfsxhNLHy]{1,2})([aiueO\.]1)', r'\g<1>2\2'),
        (r'([pbtdDcjkg\'mnqrlfsxhNLHy]{1,2})([aiueU.]1)', r'\g<1>2\2'),
        (r'^([pbtdDcjkg\'mnqrlfsxhNLHy][aiueU.][pbtdDcjkg\'mnqrlfsxhNLHy]{1,2}2)', r'1\1'),
        (r'(2[aiueU.][pbtdDcjkg\'mnqrlfsxhNLHy])2', r'\g<1>1'),
        (r'(^|[aiueU.])([pbtdDcjkg\'mnqrlfsxhNLHy][aiueU.][pbtdDcjkg\'mnqrlfsxhNLHy]2)', r'\g<1>1\2'),
        (r'([pbtdDcjkg\'mnqrlfsxhNLHy])([aiueU.]1)', r'\g<1>2\2'),
        (r'([aiueU.]([pbtdDcjkg\'mnqrlfsxhNLHy])2)[aiueU.](1\2)', r'\1.\3')],
        # degemination
        [(r'((\w)\2)i$', r'\2'),
        (r'([pbtdDcjkg\'mnqrlfsxhNLHy])\1', r'\1')],
        # fortition of unstressed high vowels
        [(r'2i1\'', 'y'),
        (r'2[uU]1\'', 'w'),
        ('1', '')],
        # elision of schwa and glottal stop, and simplification of some clusters
        [(r'2[ae.]', r''),
        (r'h(?=[pbtdDcjkg\'mnqrlfsxhNLHy])', ''),
        (r'(?<=[pbtdDcjkg\'mnqrlfsxhNLHy])h', ''),
        (r'p(?=[bdjgmnNq])', r'b'),
        (r't(?=[bdjgmnNq])', r'd'),
        (r'c(?=[bdjgmnNq])', r'j'),
        (r'k(?=[bdjgmnNq])', r'g'),
        (r'^b(?=[ptck])', r'p'),
        (r'^d(?=[ptck])', r't'),
        (r'^j(?=[ptck])', r'c'),
        (r'^g(?=[ptck])', r'k'),
        (r'^L(?=[bdjgptck])', 'l'),
        (r'(?<=^[bdjgptck])L', 'l'),
        (r'(?<=b)[mnNq]', r'm'),
        (r'(?<=d)[mnNq]', r'n'),
        (r'(?<=j)[mnNq]', r''),
        (r'(?<=g)[mnNq]', r'q'),
        (r'^pt', 'p\'t'),    # protect pt
        (r'([bdjgptck])([bdjgptck])', r'\1\1'),
        (r'^[mnNq](?=[pbmftdDcjkgnqsxNLH])', 'm'),
        (r'(?<=.)[mnNq](?=[pbfv])', 'm'),
        (r'(?<=.)[mnNq](?=[tdsz])', 'n'),
        (r'(?<=.)[mnNq](?=[cjxZ])', 'N'),
        (r'(?<=.)[mnNq](?=[kg])', 'q'),
        (r'[jd][jx]', 'j'),
        (r'[ct][cx]', r'c'),
        (r'^[cj](?=[fvsz])', r''),
        (r'(?<=^[bdjg])f', r'v'),
        (r'(?<=^[bdjg])s', r'z'),
        (r'(?<=^[bdjg])x', r'Z'),
        (r'(?<=^[cj])[rl]', r''),
        (r'^((\w)\2)', r'\2'),
        (r'\'', '')],
        # shortening of long vowels
        [(r'([aiueU])2\1', r'\1')],
    ]
    for rewrite in rewrites:
        text.sub(*rewrite)
    for batch in batches:
        old = str(text)
        for replacement in batch:
            text.sub(*replacement)
        new = str(text)
        if old != new:
            for rewrite in rewrites[::-1]:
                new = new.replace(*rewrite[::-1])
            output.append(new)
    return output

with open('c:/users/ryan/documents/tinellbianlanguages'
                '/dictionary/wordlist.json') as f:
    wordlist = map(lambda entry: entry['t'],
                filter(lambda entry: entry['l'] == 'High Lulani',
                    json.load(f)))

    wordlist = map(evolve, wordlist)
with open('c:/users/ryan/documents/tinellbianlanguages'
                '/dictionary/vulgarlulani.json', 'w') as f:
    json.dump(wordlist, f, indent=2)
