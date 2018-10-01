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
            ('&#x323;', ','),
            ('&#x2c8;', '1'),
            ('&#x2cc;', '2')]
        replacements = [
            ('nn', 'NN'),
            ('ll', 'LL'),
            ("''", "yy"),
            ("hh", "HH"),
            # frication of geminate voiced plosives, and
            # voicing of geminate voiceless plosives
            (r'bb', r'vv'),
            (r'dd', r'DD'),
            (r'gg', r'rr'),
            (r'pp', r'bb'),
            (r'tt', r'dd'),
            (r'cc', r'jj'),
            (r'kk', r'gg'),
            # umlaut
            (r'a(?=.{1,2}i)', 'e'),
            (r'u(?=.{1,2}i)', 'U'),
            # palatalisation of segments before /i/
            (r's(?=s*i)', 'x'),
            (r't(?=t*i)', 'c'),
            (r'd(?=d*i)', 'j'),
            (r'n(?=n*i)', 'N'),
            (r'l(?=l*i)', 'L'),
            # stress markers
                # C* => C*2 :: unstressed after a geminate
                # VC*V$ => VC*2V$ :: unstressed at end of word
                # 2VC*2 => 2VC* :: restress after unstressed  (*)
                # CVC*VC*2 => C2VC*VC*2 :: propagate (**)
                # (*) , (**) , (*)
            (r'(([pbvtdDcjkg\'mnqrlfsxhNLHy])\2)', r'\g<1>2'),
            (r'([aiueU.][pbvtdDcjkg\'mnqrlfsxhNLHy]+)([aiueU.])$', r'\g<1>2\2'),
            (r'(2[aiueU.][pbvtdDcjkg\'mnqrlfsxhNLHy]+)2', r'\1'),
            (r'([pbvtdDcjkg\'mnqrlfsxhNLHy])([aiueU.][pbvtdDcjkg\'mnqrlfsxhNLHy]+[aiueU.][pbvtdDcjkg\'mnqrlfsxhNLHy]+2)', r'\g<1>2\2'),
            (r'(2[aiueU.][pbvtdDcjkg\'mnqrlfsxhNLHy]+)2', r'\1'),
            (r'([pbvtdDcjkg\'mnqrlfsxhNLHy])([aiueU.][pbvtdDcjkg\'mnqrlfsxhNLHy]+[aiueU.][pbvtdDcjkg\'mnqrlfsxhNLHy]+2)', r'\g<1>2\2'),
            (r'(2[aiueU.][pbvtdDcjkg\'mnqrlfsxhNLHy]+)2', r'\1'),
            # elision of syllable final /h/
            (r'(?<=.)h(?=2)', '\''),
            # fortition of unstressed high vowels
            (r'2i\'', 'y'),
            (r'2[uU]\'', 'w'),
            # haplology middle dot
            (r'([aiueU.]([pbtdDcjkg\'mnqrlfsxhNLHy])2)[aiueU.](\2)', r'\1.\3'),
            # degemination
            (r'((\w)\2)2i$', r'\2'),
            (r'([pbvtdDcjkg\'mnqrlfsxhNLHy])\1', r'\1'),
            # simplification of vowel clusters
            (r'(?<=2a)\'(?=e)', 'y'),
            (r'(?<=[Ue])\'2i', ''),
            (r'(?<=[i])\'2u', ''),
            (r'(?<=[a])\'2U', ''),
            (r'a\'2u', 'O'),
            # elision of /y/ after palatal
            (r'(?<=[cjxNL])y', ''),
            # elision of schwa and glottal stop, and simplification of some clusters
            (r'(?<=2[iuU])', r','),
            (r'2[ae.]', r''),
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
            (r'([aiueU])2\1,*', r'\1'),
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
