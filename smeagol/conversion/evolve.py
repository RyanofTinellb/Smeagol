import re


def unique(lst):
    return [lst[0]] + [y for x, y in zip(lst, lst[1:]) if x != y]


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


class HighToDemoticLulani:
    def __init__(self, debug=False):
        self.rewrites = [
            ('&rsquo;', "'"),
            ('&middot;', '.'),
            ('&#x294;', "''"),
            ('&ouml;', 'O'),
            ('&uuml;', 'U'),
            ('&#x17e;', 'Z'),
            ('&agrave;', 'A'),
            ('&igrave;', 'I'),
            ('&ugrave;', '^'),
            ('&ograve;', '('),
            ('&egrave;', 'E'),
            ('&#x20d;', ')'),  # o with double grave
            ('&#x215;', '*'),  # u with double grave
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
            (r'(?<=[pbtdcjkgmnNqlLrfvDsx])[hH]', ''),
            (r'[hH](?=[pbtdcjkgmnNqlLrfvDsx])', ''),
            (r'[hH]([hH])', r'\1'),
            (r'([pbtdcjkg])[mnNq]', self.prenasal_assimilation),
            (r'sf|mn|pt', self.protect_cluster),
            (r'p(?=[bdjgm])|(?<=[bdjg])p', 'b'),
            (r't(?=[bdjgn])|(?<=[bdjg])t', 'd'),
            (r'c(?=[bdjgN])|(?<=[bdjg])c', 'j'),
            (r'k(?=[bdjgq])|(?<=[bdjg])k', 'g'),
            (r'[pbtdcjkg]([pbtdcjkg])', r'\1\1'),
            (r'([td])([fv])', r'\2\1'),
            ('tx', 'c'),
            ('dx', 'j'),
            (r'c(?=[lLr])', 't'),
            (r'j(?=[lLr])', 'd'),
            (r'(?<=[cj])[fsx]|(?<=D)[cj]|[fvsx](?=[cj])', ''),
            (r'[mnNq]([pbmtdncjNkgq])', self.nasal_assimilation),
            (r'n(?=[xLy])|(?<=x)n', 'N'),
            (r'N(?=[slr])|(?<=[fvD])[mnNq]|(?<=s)N', 'n'),
            (r'L(?=[tdnlscjNLx])', 'l'),
            (r'v(?=[ptk])', 'f'),
            (r'f(?=[bdg])', 'v'),
            (r'(?<=D)[pbkg]', 'D'),
            (r'([D])([td])', r'\2\1'),
            ('tD', 'tT'),
            (r'([vD])[fsx]', r'\1\1'),
            (r'[fsx]([fsx])', r'\1\1'),
            # remove /y/ after palatals, and quotes
            ('\'|(?<=[cjxNL])y', '')])
        replacements = [
            # lowering of back vowels before peripherals
            (r'u(?=[pbmfkgqhH])', 'o'),
            (r'([nl\'hbdgptck])\1', self.geminate_shift),
            (r'([auo])(?=.{1,2}i)', self.umlaut),
            (r'(([stdnl])\2?)(?=i)', self.palatalise),
            (r'.*', self.stress),
            (r'(?<=.)h(?=2)', '\''),  # elision of syllable final /h/
            (r'(?<=2a)\'(?=[aeuoUO])', 'y'),  # fortify glottal stop
            (r'(?<=2a)\'(?=[i])', 'w'),  # fortify glottal stop
            (r'2([iuUoO])\'', self.fortify_vowel),
            (r'([aiuoeOU.]([pbtdDcjkg\'mnqrlfsxhNLHy])2)[aiuoeOU.](\2)',
             r'\1.\3'),  # middot
            (r'((\w)\2)2i', r'\2'),  # kappita ==> kapta
            (r'([pbvtdDcjkg\'mnqrlfsxhNLHyw])\1', r'\1'),  # degemination
            (r'(?<!2)([aieouOU])\'2*([aieouOU])',
             self.simplify_vowel_cluster),
            (r'2([ae.])', ''),  # remove unstressed open vowels
            # (r'2', ''), # remove stress marks
            (r'.*', self.simplify_consonant_cluster),
            (r'^[mnNq](?=[pbmftdDcjkgnqsxNLH])', 'm'),
            (r'^[lL](?=[pbmftdDcjkgnqsxNLH])', 'l'),
            (r'^((\w)\2)', r'\2'),  # degeminate initials
            (r'[cj]([cj])', r'\1'),  # degeminate affricates
            (r'([aiueUoO])2\1,*', r'\1'),  # shorten long vowel
            (r'([aiueUoO])([pbmfvtdDcjkgnqsxNLH]+2[aiueUoO][pbmfvtdDcjkgnqsxNLH]+[aiueUoO]*$)',
             self.stress_antepenult),  # stress antepenultimate closed syllable when appropriate
            (r'(2[aiueUoO][pbmfvtdDcjkgnqsxNLH]+)([aiueUoO])$',
             self.stress_antepenult),  # re-write final semivowels
            (r'(?<=[^i])y$', 'i'),  # re-write final semivowels
            (r'w$', 'u'),
            (r'U$', 'O'),
            ('dd', 'd.d'),
            ('D', 'dd'),
            ('L', 'll'),
            ('N', 'nn'),
            ('H', 'hh'),
        ]
        self.evolver = Evolver(replacements, debug)
        self.debug = debug

    def evolve(self, text):
        return unique(self.evolver.evolve(
            EMString(text, self.rewrites, self.debug)
        ))

    def geminate_shift(self, regex):
        return {
            'n': 'N', 'l': 'L', '\'': 'y', 'h': 'H',
            'b': 'v', 'd': 'D', 'g': 'r', 'p': 'b',
            't': 'd', 'c': 'j', 'k': 'g',
        }[regex.group(1)] * 2

    def umlaut(self, regex):
        return dict(a='e', u='U', o='O')[regex.group(1)]

    def palatalise(self, regex):
        return dict(
            s='x', t='c', d='j', n='N', l='L'
        )[regex.group(2)] * len(regex.group(1))

    def simplify_vowel_cluster(self, regex):
        first, second = [regex.group(x) for x in range(1, 3)]
        if (first + second).lower() in ('au', 'ao'):
            return second.upper()
        if (first + second).lower() in ('ae', 'aa', 'ia', 'iu'):
            return first + 'y2' + second
        if (first + second).lower() in ('ui', 'oi'):
            return first + 'w2' + second
        return first

    def fortify_vowel(self, regex):
        if regex.group(1) == 'i':
            return 'y'
        return 'w'

    def prenasal_assimilation(self, regex):
        plosive = regex.group(1)
        return plosive + dict(
            p='m', b='m',
            t='n', d='n',
            c='N', j='N',
            k='q', g='q'
        )[plosive]

    def nasal_assimilation(self, regex):
        other = regex.group(1)
        return dict(
            p='m', b='m', m='m',
            t='n', d='n', n='n',
            c='N', j='N', N='N',
            k='q', g='q', q='q'
        )[other] + other

    def protect_cluster(self, regex):
        return '{0}\'{1}'.format(*regex.group(0))

    def setup_stresses(self, stresses):
        return [(re.compile(pattern.replace(
                'C', self.consonants).replace(
            'V', self.vowels)
        ), string) for pattern, string in stresses]

    def stress(self, regex):
        word = regex.group(0)
        for stress in (0, 1, 2):
            pattern, string = self.stresses[stress]
            word = pattern.sub(string, word)
        old = ''
        while old != word:
            old = word
            for stress in (3, 2):
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

    def stress_antepenult(self, regex):
        vowels = dict(a='A', e='E', i='I', o='(', O=')',
                      u='^', U='*')
        try:
            return vowels[regex.group(1)]
        except IndexError:
            return vowels[regex.group(0)]
