import re

def unique(lst):
    return [lst[0]] + [y for x,y in zip(lst, lst[1:]) if x != y]

class EMString:
    # Encodable mutable string
    def __init__(self, string, encoding=None, debug=False):
        self.debug = debug
        self.encoding = encoding or []
        self.external = string
        self.internal = self.encode(string)

    def sub(self, pattern, sub):
        # perform substitutions on words separately
        old = new = self.internal
        try:
            new = ' '.join(
                [pattern.sub(sub, string) for string in
                    new.split(' ')])
        except AttributeError:
            new = ' '.join(
                [re.sub(pattern, sub, string) for string in
                    new.split(' ')])
        if old != new:
            self.internal = new
            self.external = self.decode(new)
        return self.external

    def encode(self, string):
        for code in self.encoding:
            string = string.replace(*code)
        return string

    def decode(self, string):
        if not self.debug:
            string = self.nodigits(string)
        for code in self.encoding[::-1]:
            string = string.replace(*code[::-1])
        return string

    def nodigits(self, word):
        return re.sub(r'\d', '', word)

    def __str__(self):
        return self.external

class Evolver:
    def __init__(self, replacements=None, debug=False):
        replacements = replacements or []
        self.debug = debug
        self.replacements = [
            (re.compile(pattern), string) for
                pattern, string in replacements
        ]

    def evolution(self, word, replacement):
        return str(word.sub(*replacement))

    def evolve(self, word):
        output = [str(word)]
        for i, replacement in enumerate(self.replacements):
            evolution = self.evolution(word, replacement)
            output += [evolution]
        return output

class HighToVulgarLulani:
    def geminate_shift(self, regex):
        return {
            'n': 'N',
            'l': 'L',
            '\'': 'y',
            'h': 'H',
            'b': 'v',
            'd': 'D',
            'g': 'r',
            'p': 'b',
            't': 'd',
            'c': 'j',
            'k': 'g',
        }[regex.group(1)] * 2

    def umlaut(self, regex):
        return dict(a='e', u='U', o='O')[regex.group(1)]

    def palatalise(self, regex):
        return dict(
                s='x', t='c', d='j', n='N', l='L'
            )[regex.group(2)] * len(regex.group(1))

    def simplify_vowel_cluster(self, regex):
        first, second = [regex.group(x) for x in xrange(1, 3)]
        if (first + second).lower() in ('au', 'ao'):
            return 'O'
        return first

    def vowel_elision(self, regex):
        vowel = regex.group(1)
        if vowel in 'ae.':
            return ''
        else:
            return '2' + dict(i='*', u='^', U='+', o='(', O=')')[vowel]

    def __init__(self, debug=False):
        self.rewrites = [
            ('&rsquo;', "'"),
            ('&middot;', '.'),
            ('&#x294;', "''"),
            ('&eth;', 'D'),
            ('&ouml;', 'O'),
            ('&uuml;', 'U'),
            ('&ntilde;', 'N'),
            ('l&#x330;', 'L'),
            ('h&#x330;', 'H'),
            ('&#x17e;', 'Z'),
            ('&#x1ee5;', '^'), # u with dot
            ('&#x1ecd;', '('), # o with dot
            ('&#x1ecb;', '*'), # i with dot
            ('&uuml;&#x323;', '+'), # u with umlaut and dot
            ('&ouml;&#x323;', ')'), # o with umlaut and dot
            ('&#x2c8;', '1'),
            ('&#x2cc;', '2')]
        replacements = [
            # lowering of back vowels before peripherals
            (r'u(?=[pbmfkgqhH])', 'o'),
            (r'([nl\'hbdgptck])\1', self.geminate_shift),
            (r'([auo])(?=.{1,2}i)', self.umlaut),
            (r'(([stdnl])\2?)(?=i)', self.palatalise),
            # stress markers
                # C* => C*2 :: unstressed after a geminate
                # VC*V$ => VC*2V$ :: unstressed at end of word
                # 2VC*2 => 2VC* :: restress after unstressed  (*)
                # CVC*VC*2 => C2VC*VC*2 :: propagate (**)
                # (*) , (**) , (*)
            (r'(([pbvtdDcjkg\'mnqrlfsxhNLHy])\2)', r'\g<1>2'),
            (r'([aiuoeOU.][pbvtdDcjkg\'mnqrlfsxhNLHy]+)([aiuoeOU.])$', r'\g<1>2\2'),
            (r'(2[aiuoeOU.][pbvtdDcjkg\'mnqrlfsxhNLHy]+)2', r'\1'),
            (r'([pbvtdDcjkg\'mnqrlfsxhNLHy])([aiuoeOU.][pbvtdDcjkg\'mnqrlfsxhNLHy]+[aiuoeOU.][pbvtdDcjkg\'mnqrlfsxhNLHy]+2)', r'\g<1>2\2'),
            (r'(2[aiuoeOU.][pbvtdDcjkg\'mnqrlfsxhNLHy]+)2', r'\1'),
            (r'([pbvtdDcjkg\'mnqrlfsxhNLHy])([aiuoeOU.][pbvtdDcjkg\'mnqrlfsxhNLHy]+[aiuoeOU.][pbvtdDcjkg\'mnqrlfsxhNLHy]+2)', r'\g<1>2\2'),
            (r'(2[aiuoeOU.][pbvtdDcjkg\'mnqrlfsxhNLHy]+)2', r'\1'),
            # elision of syllable final /h/
            (r'(?<=.)h(?=2)', '\''),
            # fortition of unstressed high vowels
            (r'2i\'', 'y'),
            (r'2[uUoO]\'', 'w'),
            # haplology middle dot
            (r'([aiuoeOU.]([pbtdDcjkg\'mnqrlfsxhNLHy])2)[aiuoeOU.](\2)', r'\1.\3'),
            # degemination
            (r'((\w)\2)2i$', r'\2'),
            (r'([pbvtdDcjkg\'mnqrlfsxhNLHy])\1', r'\1'),
            (r'([aieouOU])\'2([aieouOU])', self.simplify_vowel_cluster),
            # elision of /y/ after palatal
            (r'(?<=[cjxNL])y', ''),
            # elision of schwa and glottal stop, and simplification of some clusters
            (r'2([ae.iuoUO])', self.vowel_elision),
            (r'h(?=[pbtdDcjkg\'mnqrlfsxhNLHy])', ''),
            (r'(?<=[pbtdDcjkg\'mnqrlfsxhNLHy])h', ''),
            (r'p(?=[bdjgmnNq])', r'b'),
            (r't(?=[bdjgmnNq])', r'd'),
            (r'c(?=[bdjgmnNq])', r'j'),
            (r'k(?=[bdjgmnNq])', r'g'),
            (r'b(?=[ptck])', r'p'),
            (r'd(?=[ptck])', r't'),
            (r'j(?=[ptck])', r'c'),
            (r'g(?=[ptck])', r'k'),
            (r'L(?=[bdjgptck])', 'l'),
            (r'(?<=[bdjgptck])L', 'l'),
            (r'(?<=b)[mnNq]', r'm'),
            (r'(?<=d)[mnNq]', r'n'),
            (r'(?<=j)[mnNq]', r''),
            (r'(?<=g)[mnNq]', r'q'),
            (r'pt', 'p\'t'),    # protect pt
            (r'([bdjgptck])([bdjgptck])', r'\1\1'),
            (r'^[mnNq](?=[pbmftdDcjkgnqsxNLH])', 'm'),
            (r'(?<=.)[mnNq](?=[pbfv])', 'm'),
            (r'(?<=.)[mnNq](?=[tdsz])', 'n'),
            (r'(?<=.)[mnNq](?=[cjxZ])', 'N'),
            (r'(?<=.)[mnNq](?=[kg])', 'q'),
            (r'[jd][jx]', 'j'),
            (r'[ct][cx]', r'c'),
            (r'[cj](?=[fvsz])', r''),
            (r'(?<=[bdjg])f', r'v'),
            (r'(?<=[bdjg])s', r'z'),
            (r'(?<=[bdjg])x', r'Z'),
            (r'(?<=[cj])[rl]', r''),
            (r'^((\w)\2)', r'\2'),
            (r'\'', ''),
            # assimilation of palatal / alveolar sounds
            (r's(?=[NL])', 'x'),
            (r'x(?=[nl])', 's'),
            (r'l(?=[xcj])', 'L'),
            (r'L(?=[std])', 'l'),
            (r'n(?=[xcj])', 'N'),
            (r'(?<=[H])n', 'N'),
            # shortening of long vowels
            (r'([aiueUoO^*()])2\1,*', r'\1'),
            # re-writing word-final semivowels
            (r'(?<=[^i])y$', 'i'),
            (r'w$', 'u')
            ]
        self.evolver = Evolver(replacements, debug)
        self.debug = debug

    def evolve(self, text):
        return unique(self.evolver.evolve(
                EMString(text, self.rewrites, self.debug)
            ))
