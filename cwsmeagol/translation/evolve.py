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

    def fortify_vowel(self, regex):
        if regex.group(1) == 'i':
            return 'y'
        return 'w'

    def setup_stresses(self, stresses):
        return [(re.compile(pattern.replace(
                'C', self.consonants).replace(
                'V', self.vowels)
            ), string) for pattern, string in stresses]

    def stress(self, regex):
        word = regex.group(0)
        for stress in (0, 1, 2, 3, 2, 3, 2):
            pattern, string = self.stresses[stress]
            word = pattern.sub(string, word)
        return word

    def setup_sandhi(self, sandhi):
        return [(re.compile(pattern), string) for pattern, string in sandhi]

    def simplify_consonant_cluster(self, regex):
        cluster = regex.group(0)
        for sandhi in self.sandhi:
            pattern, string = sandhi
            cluster = pattern.sub(string, cluster)
        return cluster

    def __init__(self, debug=False):
        self.rewrites = [
            ('&rsquo;', "'"),
            ('&middot;', '.'),
            ('&#x294;', "''"),
            ('&eth;', 'D'),
            ('&thorn;', 'T'),
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
        self.consonants = r'[pbvtdDcjkg\'mnqrlfsxhNLHy]'
        self.vowels = r'[aiuoeOU.]'
        self.stresses = self.setup_stresses([
            (r'((C)\2)', r'\g<1>2'),
            (r'(VC+)(V)$', r'\g<1>2\2'),
            (r'(2VC+)2', r'\1'),
            (r'(C)(VC+VC+2)', r'\g<1>2\2')])
        self.sandhi = self.setup_sandhi([
            (r'(?<=[cjxNL])y', ''),
            (r'h(?=[pbvtdDcjkg\'mnqrlfsxhNLHy])', ''),
            (r'(?<=[pbvtdDcjkg\'mnqrlfsxhNLHy])h', ''),
            (r'p(?=[bdjgmnNq])', r'b'),
            (r't(?=[bdjgmnNq])', r'd'),
            (r'c(?=[bdjgmnNq])', r'j'),
            (r'k(?=[bdjgmnNq])', r'g'),
            (r'b(?=[ptck])', r'p'),
            (r'v(?=[ptcksx])', r'f'),
            (r'D(?=[ptcksxrl])', r'T'),
            (r'd(?=[ptck])', r't'),
            (r'j(?=[ptck])', r'c'),
            (r'g(?=[ptck])', r'k'),
            (r'(?<=[vD])q', 'n'),
            (r'(?<=[TD])c', 't'),
            (r'(?<=[TD])j', 'd'),
            (r'([fv])([pb])', r'\2\1'),
            (r'([DT])([td])', r'\2\1'),
            (r'L(?=[bdjgptck])', 'l'),
            (r'(?<=[bdjgptck])L', 'l'),
            (r'(?<=b)[mnNq]', r'm'),
            (r'(?<=d)[mnNq]', r'n'),
            (r'(?<=j)[mnNq]', r''),
            (r'(?<=g)[mnNq]', r'q'),
            (r'pt', 'p\'t'),    # protect pt
            (r'mn', 'm\'n'),    # protect mn
            (r'sf', 's\'f'),    # protect sf
            (r'([bdjgptck])([bdjgptck])', r'\1\1'),
            (r'(?<=.)[mnNq](?=[pbfv])', 'm'),
            (r'(?<=.)[mnNq](?=[tdsz])', 'n'),
            (r'(?<=.)[mnNq](?=[cjxZ])', 'N'),
            (r'(?<=.)[mnNq](?=[kg])', 'q'),
            (r'[jd][jx]', 'j'),
            (r'[ct][cx]', r'c'),
            (r'[cj](?=[fvsz])', r''),
            (r'(?<=[bvdDjg])f', r'v'),
            (r'f(?=[djg])', r'v'),
            (r'[fvszxZ](?=[cj])', ''),
            (r'(?<=[bdjg])s', r'z'),
            (r's(?=[bdjg])', r'z'),
            (r'(?<=[bdjg])x', r'Z'),
            (r'x(?=[bdjg])', r'Z'),
            (r'(?<=[cj])[rl]', r''),
            (r'\'', ''),
            (r's(?=[NLx])', 'x'),
            (r'(?<=[H])s', 'x'),
            (r'x(?=[nls])', 's'),
            (r'l(?=[xcj])', 'L'),
            (r'(?<=[HL])l', 'L'),
            (r'L(?=[stdr])', 'l'),
            (r'n(?=[xcj])', 'N'),
            (r'(?<=[H])n', 'N')])
        replacements = [
            (r'u(?=[pbmfkgqhH])', 'o'), # lowering of back vowels before peripherals
            (r'([nl\'hbdgptck])\1', self.geminate_shift),
            (r'([auo])(?=.{1,2}i)', self.umlaut),
            (r'(([stdnl])\2?)(?=i)', self.palatalise),
            (r'.*', self.stress),
            (r'(?<=.)h(?=2)', '\''), # elision of syllable final /h/
            (r'2([iuUoO])\'', self.fortify_vowel),
            (r'([aiuoeOU.]([pbtdDcjkg\'mnqrlfsxhNLHy])2)[aiuoeOU.](\2)', r'\1.\3'), # middot
            (r'((\w)\2)2i', r'\2'), # kappita ==> kapta
            (r'([pbvtdDcjkg\'mnqrlfsxhNLHyw])\1', r'\1'), # degemination
            (r'([aieouOU])\'2([aieouOU])', self.simplify_vowel_cluster),
            (r'2([ae.iuoUO])', self.vowel_elision),
            (r'[pbvtdDcjkg\'mnqrlfsxhNLHyw]{2}', self.simplify_consonant_cluster),
            (r'^[mnNq](?=[pbmftdDcjkgnqsxNLH])', 'm'),
            (r'^((\w)\2)', r'\2'), # degeminate initials
            (r'([aiueUoO^*()])2\1,*', r'\1'), # shorten long vowel
            (r'(?<=[^i])y$', 'i'), # re-write final semivowels
            (r'w$', 'u')]
        self.evolver = Evolver(replacements, debug)
        self.debug = debug

    def evolve(self, text):
        return unique(self.evolver.evolve(
                EMString(text, self.rewrites, self.debug)
            ))
