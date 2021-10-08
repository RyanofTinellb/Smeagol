import re
from itertools import chain
from .translator import Translator
from ..utilities import filesystem as fs, utils

class Linker:
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
        match attr:
            case 'link_adders':
                self.link_adders = {}
                return self.link_adders
            case default:
                return utils.default_getter(self, attr)

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
        self.glossary = fs.load(filename)
        self.tooltip = ('<span class="tooltip">'
                        '<small-caps>{0}</small-caps>'
                        '<span class="tooltip-text">{1}</span>'
                        '</span>')
        self.filename = filename

    def __str__(self):
        return self._file

    def refresh(self, filename=''):
        self._file = filename
        self.glossary = fs.load(filename)

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
        with utils.ignored(IndexError, AttributeError):
            self.language = entry.matriarch.url
        return re.sub(r'<{0}>(.*?)</{0}>'.format('[bl]ink'), self._link, text)

    def _link(self, matchobj):
        word = matchobj.group(1).split(':')
        tr = self.translator
        lang = utils.urlform(self.language if len(word) == 1 else tr.select(word[0]))
        word = word[-1]
        link = utils.urlform(utils.sellCaps(word))
        try:
            initial = utils.page_initial(link)
        except IndexError:
            return word
        return '<a href="{0}/{1}/{2}.html#{3}">{4}</a>'.format(
            self.url, initial, link, lang, word)

    def remove_links(self, text, entry):
        """
        text: 'foo<a href="url/b/bar.html#language">bar</a>baz' =>
                    'foo<link>bar</link>baz'

        """
        with utils.ignored(IndexError, AttributeError):
            self.language = entry.matriarch.url
        regex = fr'<a href="{self.url}.*?#(.*?)">(.*?)</a>'
        return re.sub(regex, self._unlink, text)

    def _unlink(self, regex):
        tr = self.translator
        lang, link = [regex.group(x) for x in range(1,3)]
        tag = 'link' if not self.wordlist or link in self.wordlist else 'bink'
        if lang == utils.urlform(self.language):
            return '<{0}>{1}</{0}>'.format(tag, link)
        return '<{0}>{1}:{2}</{0}>'.format(tag, tr.encode(lang), link)

    def wordlist_setup(self):
        wordlist = fs.load(self.wordlist_file)
        self.wordlist = [word['t'] for word in wordlist]

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
        language = utils.urlform(self.language if len(word) == 1 else tr.select(word[0]))
        link = utils.urlform(utils.sellCaps(word[-1]))
        initial = utils.page_initial(link)
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
        if language == utils.urlform(self.language):
            return r'<{0}>{1}</{0}>'.format(tag, link)
        return r'<{0}>{1}:{2}</{0}>'.format(tag, tr.encode(language), link)

    def wordlist_setup(self):
        wordlist = fs.load(self.wordlist_file)
        self.wordlist = [word['t'] for word in wordlist]

    def refresh(self, text=''):
        self.wordlist_setup()

class ExternalGrammar:
    def __init__(self, filename, wordlist=None, translator=None):
        self.adder = {'ExternalGrammar': filename}
        self.replacements = fs.load(filename)
        self.url = self.replacements['url']
        self.language = None
        self.filename = filename

    def __str__(self):
        return self._file

    def refresh(self, filename=''):
        self._file = filename
        self.replacements = fs.load(self.filename)

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
        with utils.ignored(KeyError):
            link = self.replacements['languages'][self.language][pos]
            try:
                notwith = link.get('not with', [])
                link = link.get('link', '')
            except AttributeError:
                notwith = []
            show = self.poses.isdisjoint(notwith)
            show = '{0}' if show else '<span class="hidden">{0}</span>'
            if link:
                language = utils.urlform(self.language)
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
