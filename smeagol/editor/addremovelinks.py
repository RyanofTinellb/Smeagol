import re
import json
from itertools import chain
from smeagol import Translator
from smeagol.utils import urlform, ignored, buyCaps, sellCaps

class AddRemoveLinks:
    def __init__(self, link_adders):
        self += link_adders

    @property
    def adders(self):
        chain_up = chain.from_iterable
        adders = [adder.adder for adder in self.link_adders.values()]
        return dict(chain_up(adder.iteritems() for adder in adders))

    def __add__(self, adder):
        for adder, resource in adder.iteritems():
            self.link_adders[adder] = globals()[adder](resource)
        return self

    def __sub__(self, adder):
        for adder, resource in adder.iteritems():
            self.link_adders.pop(adder, None)
        return self

    def __getattr__(self, attr):
        if attr == 'link_adders':
            self.link_adders = {}
            return self.link_adders
        else:
            raise AttributeError(
                'AddRemoveLinks has no attribute {0}'.format(attr))

    def add_links(self, text, entry):
        for link_adder in self.link_adders.values():
            text = link_adder.add_links(text, entry)
        return text

    def remove_links(self, text):
        for link_adder in self.link_adders.values():
            text = link_adder.remove_links(text)
        return text

    def string(self, adder):
        return str(self.link_adders[adder])

    def refresh(self, text, adder):
        self.link_adders[adder].refresh(text)


class Glossary:
    def __init__(self, filename):
        self.adder = {'Glossary': filename}
        try:
            with open(filename) as glossary:
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
        with open(self.filename, 'w') as f:
            f.write(new_file)
        self.glossary = json.loads(new_file)

    def add_links(self, text, entry):
        for abbrev, full_form in self.glossary.iteritems():
            text = text.replace(
                '<small-caps>{0}</small-caps>'.format(abbrev),
                                self.tooltip.format(abbrev, full_form))
        return text

    def remove_links(self, text):
        for abbrev, full_form in self.glossary.iteritems():
            text = text.replace(self.tooltip.format(abbrev, full_form),
                '<small-caps>{0}</small-caps>'.format(abbrev))
        return text


class ExternalDictionary:
    def __init__(self, url):
        self.url = url
        self.language = ''
        self.adder = {'ExternalDictionary': url}

    def add_links(self, text, entry):
        """
        text: 'foo<link>bar</link>baz' =>
            'foo<a href="url/b/bar.html#language">bar</a>baz'
        """
        self.language = '#'
        with ignored(IndexError):
            self.language += entry.matriarch.url
        return re.sub(r'<{0}>(.*?)</{0}>'.format('link'), self._link, text)

    def _link(self, matchobj):
        word = matchobj.group(1)
        link = urlform(word)
        try:
            initial = re.findall(r'\w', link)[0]
        except IndexError:
            return word
        return '<a href="{0}/{1}/{2}.html{3}">{4}</a>'.format(
            self.url, initial, link, self.language, word)

    def remove_links(self, text):
        """
        text: 'foo<a href="url/b/bar.html#language">bar</a>baz' =>
                    'foo<link>bar</link>baz'

        """
        return re.sub(r'<a href="{0}.*?>(.*?)</a>'.format(self.url), r'<{0}>\1</{0}>'.format('link'), text)


class InternalDictionary:
    def __init__(self, resource=None):
        self.adder = {'InternalDictionary': resource}
        self.translator = Translator()

    def add_links(self, text, entry):
        """
        Add links of the form
            '<a href="../b/blah.html#highlulani">blah</a>'
        """
        self.language = 'also'
        lang = '1]'  # language marker
        output = []
        regex = r'<{0}>(.*?)</{0}>'.format('link')
        for line in text.split('['):
            if lang in line:
                self.language = re.sub(lang + '(.*?)\n', r'\1', line)
            output.append(re.sub(regex, self._link, line))
        return '['.join(output)

    def _link(self, text):
        word = text.group(1).split(':')
        tr = self.translator
        language, link = [urlform(name) for name in (
            self.language if len(word) == 1 else tr.select(word[0]),
            sellCaps(word[-1])
        )]
        initial = re.findall(r'\w', link)[0]
        return '<a href="../{0}/{1}.html#{2}">{3}</a>'.format(
            initial, link, language, word[-1])

    def remove_links(self, text):
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
        language, link = [regex.group(x) for x in xrange(1,3)]
        if language == urlform(self.language):
            return r'<{0}>{1}</{0}>'.format('link', link)
        return r'<{0}>{1}:{2}</{0}>'.format('link', tr.encode(language), link)


class ExternalGrammar:
    def __init__(self, filename):
        self.adder = {'ExternalGrammar': filename}
        with open(filename) as replacements:
            self._file = replacements.read()
        self.replacements = json.loads(self._file)
        self.url = self.replacements['url']
        self.language = None
        self.filename = filename

    def __str__(self):
        return self._file

    def refresh(self, new_file=''):
        self._file = new_file
        with open(self.filename, 'w') as f:
            f.write(new_file)
        self.replacements = json.loads(new_file)

    def add_links(self, text, entry):
        """
        '<a href="http://grammar.tinellb.com/highlulani/
                                            morphology/nouns">noun</a>'
        """
        div = ' <div class="definition">'
        lang = '1]'  # language marker
        wcs = '3]'  # word classes marker
        output = []
        for line in text.split('['):
            if line.startswith(lang):
                self.language = line[len(lang):-1]
            elif line.startswith(wcs):
                try:
                    pos, rest = line[len(wcs):].split(div, 1)  # part of speech
                except ValueError:
                    pos, rest = line[len(wcs):], ''
                self.poses = set(re.sub(r'\(.*?\)', '', pos).split(' '))
                pos = ''.join(map(self._link, re.split(r'([^a-zA-Z0-9_\'-])', pos)))
                line = wcs + pos + div + rest
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

    def remove_links(self, text):
        """
        text: 'foo<a href="url/b/bar.html#language">bar</a>baz' =>
                    'foo<link>bar</link>baz'

        Grammar markdown file takes care of adding and removing links to the phonology page

        """
        return '['.join(map(self._unlink, text.split('[')))

    def _unlink(self, line):
        div = ' <div class="definition">'
        wcs = '3]'
        if line.startswith(wcs):
            try:
                pos, rest = line[len(wcs):].split(div, 1)
            except ValueError:
                pos, rest = line[len(wcs):], ''
            pos = re.sub(r'<span class="hidden">(.*?)</span>', r'\1', pos)
            pos = re.sub(r'<a href=.*?>(.*?)</a>', r'\1', pos)
            return wcs + pos + div + rest
        else:
            return line
