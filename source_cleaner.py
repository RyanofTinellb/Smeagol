import html
import re

from smeagol.conversion.translator import Translator
from smeagol import file_system as fs

sylls = {"p": "パ", "b": "バ", "m": "マ", "f": "ヘ", "P": "ピ", "B": "ビ", "M": "ミ", "F": "ベ", "o": "プ", "O": "ブ", "U": "ム", "v": "フ", "t": "タ", "d": "ダ", "n": "ナ", "l": "ワ", "r": "ラ", "s": "サ", "T": "テ", "D": "デ", "N": "ニ", "L": "エ", "R": "リ", "S": "セ", "e": "ト", "E": "ヅ", "I": "ヌ", "W": "ヲ", "w": "ル",
         "z": "ス", "c": "ヤ", "j": "ヂ", "x": "ザ", "C": "チ", "J": "ジ", "X": "シ", "y": "ユ", "Y": "ヨ", "Z": "ズ", "k": "カ", "g": "ガ", "q": "ゲ", "K": "キ", "G": "ギ", "Q": "ネ", "$": "ク", "%": "グ", "A": "モ", "a": "ア", "h": "ハ", "i": "イ", "H": "ヒ", "u": "ウ", "V": "ホ", ";": "ッ", "/": "・", ".": "。", " ": " ", ",": "、"}
translator = Translator('hl')


class Line:
    def __init__(self, line, tags, block, folding, repeat):
        self._line = line
        self.tags = tags
        self.block = block
        self.folding = folding
        self.repeat = repeat

    def __str__(self):
        return self.line

    def match(self, regex):
        return re.match(regex, self._line, re.S | re.M)

    def search(self, regex):
        return re.search(regex, self._line, re.S | re.M)

    def replace(self, regex, repl):
        self._line = re.sub(regex, repl, self._line, flags=re.S | re.M)
        return self._line

    def syll(self, match):
        word = match.group(1).replace('&gt;', '$').replace('&lt;', '%')
        try:
            word = ''.join([sylls[char] for char in word])
        except KeyError:
            word = translator.convert_text(word)
            word = ''.join([sylls[char] for char in word])
        tl = 'tinellbian-hl'
        return f'<{tl}>{word}</{tl}>'

    @property
    def line(self):
        if self.repeat:
            print('-----------------------------')
            print(self._line)
            self.repeat.off()
        self.replace(r'<a href=\"(?:http://dic.*?|\.\.)/.*?\.html#highlulani\">(.*?)</a>',
                     r'<link-hl>\1</link-hl>')
        self.replace(r'<high-lulani>(.*?)</high-lulani>', self.syll)
        self.replace(
            r'<span class=\"tooltip\"><small-caps>(.*?)</small-caps><span class=\"tooltip-text\">.*?</span></span>',
            r'<abbr>\1</abbr>')
        self.replace(r'<span class=\"(.*?)\">(.*?)</span>', r'<\1>\2</\1>')
        self.replace(r'\[(e|f) \]', r'[\1]')
        if match := self.match(r'\[d (.*?)\]'):
            self.div(match)
        elif match := self.match(r'\[/d\]'):
            self.undiv(match)
        elif match := self.match(r'\[/t\]'):
            self._line = '</table>'
        elif match := self.match(r'\[/n\]'):
            self._line = '</ol>'
        elif match := self.match(r'\[/l\]'):
            self._line = '</ul>'
        elif match := self.match(r'\[t\](.*)'):
            self.table(match)
        elif match := self.match(r'\[([ln])\](.*)'):
            self.list_(match)
        elif match := self.match(r'\[(\d)\](.*)'):
            self.heading(match)
        elif self.folding:
            self.emstrong()
        if self.block and not self.match(r'\[[ef]\]'):
            self.unefblock()
        elif match := self.match(r'\[f\](.*)'):
            self.efblock(match)
        self.unescape()
        self.replace(r'\[e\]', r'')
        return self._line
    
    def list_(self, match):
        kind = dict(l='ul', n='ol')[match.group(1)]
        text = match.group(2)
        self._line = f'<{kind}>{text}'

    def table(self, match):
        self._line = f'<table>{match.group(1)}'
    
    def efblock(self, match):
        self.block.on()
        self._line = f'<block>{match.group(1)}'
    
    def unefblock(self):
        self.block.off()
        self._line = f'</block>{self._line}'
        
    def unescape(self):
        self.replace('&gt;', '+greater-than+')
        self.replace('&lt;', '+less-than+')
        self._line = html.unescape(self._line)
        self.replace(r'\+greater-than\+', '&gt;')
        self.replace(r'\+less-than\+', '&lt;')

    def emstrong(self):
        self.replace('<strong>', '<transliteration-hl>')
        self.replace('</strong>', '</transliteration-hl>')
        if self.search(r'</*em>'):
            self.replace(r'</*em>', '')
            self._line = f'<gloss>{self._line}</gloss>'
            self.replace(r'<gloss>\[e\]', '[e]<gloss>')

    def div(self, match):
        kind = match.group(1)
        self.tags.append(kind)
        if kind == 'folding':
            self.folding.on()
        self._line = f'<{kind}>'

    def undiv(self, match):
        try:
            kind = self.tags.pop()
            if kind == 'folding':
                self.folding.off()
            self._line = f'</{kind}>'
        except IndexError:
            self.repeat.on()

    def heading(self, match):
        number = k if (k := int(match.group(1))
                       ) <= 6 else f'6 class="level-{k}'
        heading = match.group(2)
        self._line = f'<h{number}>{heading}</h{number}>'
        if number == 2:
            self.replace(r'<a href=\"http://grammar.tinellb.com.*?\">(.*?)</a>', r'<poslink>\1</poslink>')


class Mode:
    def __init__(self, state=False):
        self.state = state

    def on(self):
        self.state = True

    def off(self):
        self.state = False

    def __bool__(self):
        return self.state


def clean(page):
    tags = []
    modes = dict(block=Mode(), folding=Mode(), repeat=Mode())
    text = '['.join(page.text).replace('[', '\n[').splitlines()
    if text and re.match(r'(?:[1-9ef]\]|d )', text[0]):
        text[0] = '[' + text[0]
    text = '\n'.join([str(Line(line, tags, **modes)) for line in text if line])
    text = re.sub(r'(<[a-z-]*>)\n', r'\1', text, re.M|re.S)
    text = re.sub(r'\n(</[a-z-]*>)', r'\1', text, re.M|re.S)
    if tags:
        print(f'{page.name} still has tags {tags}')
    page.text = text
