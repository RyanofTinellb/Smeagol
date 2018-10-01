import re
import json
from cwsmeagol.utils import urlform, ignored, buyCaps, sellCaps

class AddRemoveLinks:
    def __init__(self, link_adders):
        """
        Allow for the removal of all links, and addition of specific
            links to Smeagol pages

        :param link_adders: (obj[]) a list of link adder instances
        """
        self.link_adders = link_adders

    def add_links(self, text, entry):
        for link_adder in self.link_adders:
            text = link_adder.add_links(text, entry)
        return text

    def remove_links(self, text):
        for link_adder in self.link_adders:
            text = link_adder.remove_links(text)
        return text


class Glossary:
    def __init__(self, filename):
        try:
            with open(filename) as glossary:
                self.glossary = json.load(glossary)
        except IOError:
            self.glossary = {}
        self.tooltip = ('<span class="tooltip">'
                        '<small-caps>{0}</small-caps>'
                        '<span class="tooltip-text">{1}</span>'
                        '</span>')

    def add_links(self, text, entry):
        for abbrev, full_form in self.glossary.iteritems():
            text = text.replace('<small-caps>{0}</small-caps>'.format(abbrev),
                                self.tooltip.format(abbrev, full_form))
        return text

    def remove_links(self, text):
        for abbrev, full_form in self.glossary.iteritems():
            text = text.replace(self.tooltip.format(abbrev, full_form),
                                '<small-caps>{0}</small-caps>'.format(abbrev))
        return text


class ExternalDictionary:
    """
    Move between markdown links and links to an external dictionary site

    :param text: (str) The source text
    :param url: (str) A url to the top page of the external site
    """

    def __init__(self, url):
        self.url = url
        self.language = ''

    def add_links(self, text, entry):
        """
        Replace links in text with hyperlinks to an external dictionary site

        text: 'foo<link>bar</link>baz' =>
            'foo<a href="url/b/bar.html#language">bar</a>baz'

        """
        self.language = '#'
        with ignored(IndexError):
            self.language += entry.ancestors[1].urlform
        return re.sub(r'<{0}>(.*?)</{0}>'.format('link'), self._link, text)

    def _link(self, matchobj):
        word = matchobj.group(1)
        link = urlform(word)
        try:
            initial = re.findall(r'\w', link)[0]
        except IndexError:
            print(link)
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
    """
    Replace links with hyperlinks to other entries in the same dictionary
    """
    def add_links(self, text, entry):
        """
        Add links of the form
            '<a href="../b/blah.html#highlulani">blah</a>'
        """
        self.language = 'also'
        div = ' <div class="definition">'
        lang = '[2]'  # language marker
        output = []
        regex = r'<{0}>(.*?)</{0}>'.format('link')
        for line in text.splitlines():
            if line.startswith(lang):
                self.language = line[len(lang):]
            output.append(re.sub(regex, self._link, line))
        return '\n'.join(output)

    def _link(self, text):
        word = text.group(1).split(':')
        language = urlform(self.language if len(word) == 1 else word[0])
        link = urlform(word[-1])
        initial = re.findall(r'\w', link)[0]
        return '<a href="../{0}/{1}.html#{2}">{3}</a>'.format(
            initial, link, language, buyCaps(word[-1]))

    def remove_links(self, text):
        regex = r'<a href="(?:\w+\.html|\.\./.*?)">(.*?)</a>'
        return re.sub(regex, self._unlink, text)

    def _unlink(self, regex):
        return r'<{0}>{1}</{0}>'.format('link', sellCaps(regex.group(1)))


class ExternalGrammar:
    """
    Replace given words in parts of speech with external URLs.
    :param filename (str): filename to get replacements from.
    """

    def __init__(self, filename):
        with open(filename) as replacements:
            self.replacements = json.load(replacements)
        self.url = self.replacements['url']
        self.language = None

    def add_links(self, text, entry):
        """
        Add links of the form
            '<a href="http://grammar.tinellb.com/highlulani/morphology/nouns">noun</a>'
        """
        div = ' <div class="definition">'
        lang = '[2]'  # language marker
        wcs = '[5]'  # word classes marker
        output = []
        for line in text.splitlines():
            if line.startswith(lang):
                self.language = line[len(lang):]
            elif line.startswith(wcs):
                try:
                    pos, rest = line[len(wcs):].split(div, 1)  # part of speech
                except ValueError:
                    pos, rest = line[len(wcs):], ''
                pos = ''.join(map(self._link, re.split(r'([^a-zA-Z0-9_\'-])', pos)))
                line = wcs + pos + div + rest
            output.append(line)
        return '\n'.join(output)

    def _link(self, pos):
        if re.match('\W+|rarr', pos):
            return pos
        with ignored(KeyError):
            link = self.replacements['languages'][self.language][pos]
            language = urlform(self.language)
            return '<a href="{0}/{1}/{2}">{3}</a>'.format(self.url, language, link, pos)
        return pos

    def remove_links(self, text):
        """
        text: 'foo<a href="url/b/bar.html#language">bar</a>baz' =>
                    'foo<link>bar</link>baz'

        Grammar markdown file takes care of adding and removing links to the phonology page

        """
        return '\n'.join(map(self._unlink, text.splitlines()))

    def _unlink(self, line):
        div = ' <div class="definition">'
        wcs = '[5]'
        if line.startswith(wcs):
            try:
                pos, rest = line[len(wcs):].split(div, 1)
            except ValueError:
                pos, rest = line[len(wcs):], ''
            pos = re.sub(r'<a href=.*?>(.*?)</a>', r'\1', pos)
            return wcs + pos + div + rest
        else:
            return line
