import re
import json
from itertools import chain
from smeagol import Translator
from ..utils import urlform, ignored, buyCaps, sellCaps, page_initial

class AddRemoveLinks:
    def __init__(self, link_adders=None, wordlist=None, translator=None):
        self.wordlist = wordlist or ''
        self.translator = translator or Translator()
        if link_adders:
            self += link_adders

    @property
    def adders(self):
        chain_up = chain.from_iterable
        adders = [adder.adder for adder in list(self.link_adders.values())]
        return dict(chain_up(iter(adder.items()) for adder in adders))

    def __add__(self, adder):
        for adder, resource in adder.items():
            args = self.wordlist, self.translator
            self.link_adders[adder] = globals()[adder](resource, *args)
        return self

    def __sub__(self, adder):
        for adder, resources in adder.items():
            self.link_adders.pop(adder, None)
        return self

    def __getattr__(self, attr):
        if attr == 'link_adders':
            self.link_adders = {}
            return self.link_adders
        else:
            raise AttributeError(f'AddRemoveLinks has no attribute {attr}')

    def add_links(self, text, entry):
        for link_adder in list(self.link_adders.values()):
            text = link_adder.add_links(text, entry)
        return text

    def remove_links(self, text, entry):
        for link_adder in list(self.link_adders.values()):
            text = link_adder.remove_links(text, entry)
        return text

    def string(self, adder):
        return str(self.link_adders[adder])

    def refresh(self, text, adder):
        self.link_adders[adder].refresh(text)


class Glossary:
    def __init__(self, filename, wordlist=None, translator=None):
        self.adder = {'Glossary': filename}
        try:
            with open(filename, encoding='utf-8') as glossary:
                self._file = glossary.read()
            self.glossary = json.loads(self._file)
        except IOError:
            self.glossary = {}
        self.tooltip = ('<span class="tooltip">'
                        '<small-caps>{0}</small-caps>'
                        '<span class="tooltip-text">{1}</span>'
                        '</span>')
        self.filename = filename

    def __str__(self):
        return self._file

    def refresh(self, new_file=''):
        self._file = new_file
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write(new_file)
        self.glossary = json.loads(new_file)

    def add_links(self, text, entry):
        for abbrev, full_form in self.glossary.items():
            text = text.replace(
                f'<small-caps>{abbrev}</small-caps>',
                self.tooltip.format(abbrev, full_form))
        return text

    def remove_links(self, text, entry):
        for abbrev, full_form in self.glossary.items():
            text = text.replace(self.tooltip.format(abbrev, full_form),
                f'<small-caps>{abbrev}</small-caps>')
        return text


class ExternalDictionary:
    def __init__(self, url, wordlist=None, translator=None):
        self.url = url
        self.wordlist_file = wordlist
        self.language = ''
        self.adder = {'ExternalDictionary': url}
        self.wordlist_setup()
        self.translator = translator or Translator()

    def add_links(self, text, entry):
        """
        text: 'foo<link>bar</link>baz' =>
            'foo<a href="url/b/bar.html#language">bar</a>baz'
        """
        with ignored(IndexError, AttributeError):
            self.language = entry.matriarch.url
        return re.sub(r'<{0}>(.*?)</{0}>'.format('[bl]ink'), self._link, text)

    def _link(self, matchobj):
        word = matchobj.group(1).split(':')
        tr = self.translator
        lang = urlform(self.language if len(word) == 1 else tr.select(word[0]))
        word = word[-1]
        link = urlform(sellCaps(word))
        try:
            initial = page_initial(link)
        except IndexError:
            return word
        return '<a href="{0}/{1}/{2}.html#{3}">{4}</a>'.format(
            self.url, initial, link, lang, word)

    def remove_links(self, text, entry):
        """
        text: 'foo<a href="url/b/bar.html#language">bar</a>baz' =>
                    'foo<link>bar</link>baz'

        """
        with ignored(IndexError, AttributeError):
            self.language = entry.matriarch.url
        regex = fr'<a href="{self.url}.*?#(.*?)">(.*?)</a>'
        return re.sub(regex, self._unlink, text)

    def _unlink(self, regex):
        tr = self.translator
        lang, link = [regex.group(x) for x in range(1,3)]
        tag = 'link' if not self.wordlist or link in self.wordlist else 'bink'
        if lang == urlform(self.language):
            return '<{0}>{1}</{0}>'.format(tag, link)
        return '<{0}>{1}:{2}</{0}>'.format(tag, tr.encode(lang), link)

    def wordlist_setup(self):
        if self.wordlist_file:
            with open(self.wordlist_file, encoding='utf-8') as wordlist:
                wordlist = json.load(wordlist)
            self.wordlist = [word['t'] for word in wordlist]
        else:
            self.wordlist = None

    def refresh(self, text=''):
        self.wordlist_setup()


class InternalDictionary:
    def __init__(self, resource=None, wordlist=None, translator=None):
        self.adder = {'InternalDictionary': resource}
        self.translator = translator or Translator()
        self.wordlist_file = wordlist
        self.wordlist_setup()

    def add_links(self, text, entry):
        """
        Add links of the form
            '<a href="../b/blah.html#highlulani">blah</a>'
        """
        self.language = 'also'
        lang = '1]'  # language marker
        output = []
        regex = r'<{0}>(.*?)</{0}>'.format('[bl]ink')
        for line in text.split('['):
            if lang in line:
                self.language = re.sub(lang + '(.*?)\n', r'\1', line)
            output.append(re.sub(regex, self._link, line))
        return '['.join(output)

    def _link(self, text):
        word = text.group(1).split(':')
        tr = self.translator
        language = urlform(self.language if len(word) == 1 else tr.select(word[0]))
        link = urlform(sellCaps(word[-1]))
        initial = page_initial(link)
        return '<a href="../{0}/{1}.html#{2}">{3}</a>'.format(
            initial, link, language, word[-1])

    def remove_links(self, text, entry):
        self.language = 'also'
        lang = '1]'  # language marker
        output = []
        regex = r'<a href="(?:\w+\.html|\.\./.*?)#(.*?)">(.*?)</a>'
        for line in text.split('['):
            if lang in line:
                self.language = re.sub(lang + '(.*?)\n', r'\1', line)
            output.append(re.sub(regex, self._unlink, line))
        return '['.join(output)

    def _unlink(self, regex):
        tr = self.translator
        language, link = [regex.group(x) for x in range(1,3)]
        tag = 'link' if not self.wordlist or link in self.wordlist else 'bink'
        if language == urlform(self.language):
            return r'<{0}>{1}</{0}>'.format(tag, link)
        return r'<{0}>{1}:{2}</{0}>'.format(tag, tr.encode(language), link)

    def wordlist_setup(self):
        if self.wordlist_file:
            with open(self.wordlist_file, encoding='utf-8') as wordlist:
                wordlist = json.load(wordlist)
            self.wordlist = [word['t'] for word in wordlist]
        else:
            self.wordlist = None

    def refresh(self, text=''):
        self.wordlist_setup()

class ExternalGrammar:
    def __init__(self, filename, wordlist=None, translator=None):
        self.adder = {'ExternalGrammar': filename}
        with open(filename, encoding='utf-8') as replacements:
            self._file = replacements.read()
        self.replacements = json.loads(self._file)
        self.url = self.replacements['url']
        self.language = None
        self.filename = filename

    def __str__(self):
        return self._file

    def refresh(self, new_file=''):
        self._file = new_file
        with open(self.filename, 'w', encoding='utf-8') as f:
            f.write(new_file)
        self.replacements = json.loads(new_file)

    def add_links(self, text, entry):
        """
        '<a href="http://grammar.tinellb.com/highlulani/
                                            morphology/nouns">noun</a>'
        """
        lang = '1]'  # language marker
        wcs = '2]'  # word classes marker
        output = []
        for line in text.split('['):
            if line.startswith(lang):
                self.language = line[len(lang):-1]
            elif line.startswith(wcs):
                pos = line[len(wcs):-1]
                self.poses = set(re.sub(r'\(.*?\)', '', pos).split(' '))
                pos = ''.join(map(self._link, re.split(r'([^a-zA-Z0-9_\'-])', pos)))
                line = wcs + pos + '\n'
            output.append(line)
        return '['.join(output)

    def _link(self, pos):
        if re.match('\W+|rarr', pos):
            return pos
        with ignored(KeyError):
            link = self.replacements['languages'][self.language][pos]
            try:
                notwith = link.get('not with', [])
                link = link.get('link', '')
            except AttributeError:
                notwith = []
            show = self.poses.isdisjoint(notwith)
            show = '{0}' if show else '<span class="hidden">{0}</span>'
            if link:
                language = urlform(self.language)
                href = '<a href="{0}/{1}/{2}">{3}</a>'
                pos = href.format(self.url, language, link, pos)
            return show.format(pos)
        return pos

    def remove_links(self, text, entry):
        """
        text: 'foo<a href="url/b/bar.html#language">bar</a>baz' =>
                    'foo<link>bar</link>baz'

        Grammar markdown file takes care of adding and removing links to the phonology page

        """
        return '['.join(map(self._unlink, text.split('[')))

    def _unlink(self, line):
        wcs = '2]'
        if line.startswith(wcs):
            pos = line[len(wcs):-1]
            pos = re.sub(r'<span class="hidden">(.*?)</span>', r'\1', pos)
            pos = re.sub(r'<a href=.*?>(.*?)</a>', r'\1', pos)
            return wcs + pos + '\n'
        else:
            return line
