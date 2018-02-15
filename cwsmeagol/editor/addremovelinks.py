import re
import json
from cwsmeagol.utils import urlform, ignored

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
        initial = re.findall(r'\w', link)[0]
        return '<a href="{0}/{1}/{2}.html{3}">{4}</a>'.format(
                self.url, initial, link, self.language, word)

    def remove_links(self, text):
        """
        text: 'foo<a href="url/b/bar.html#language">bar</a>baz' =>
                    'foo<link>bar</link>baz'

        """
        return re.sub(r'<a href="{0}.*?>(.*?)</a>'.format(self.url), r'<{0}>\1</{0}>'.format('link'), text)


class InternalStory:
    def add_links(self, text, entry):
        """
        Add version links to the each paragraph of the text

        :param entry: (Page)
        :param text: (str)
        :return: (str)
        """
        if entry.name is None:
            return ''
        paragraphs = text.splitlines()
        version = entry.ancestors[1].name
        for uid, paragraph in enumerate(paragraphs[1:], start=1):
            if paragraph == '<span class="stars">* * *</span>':
                pass
            elif version == 'Gloss':
                 paragraph = '{0}' + paragraphs[uid].replace(' | [r]', '{1} | [r]')
            elif version == 'Interlinear':
                paragraph = '[t]{0}'
                regex = r'(?= \| \[r\]<div class=\"literal\">)'
                paragraph += re.sub(regex, '{1}', paragraphs[uid][3:])
            else:
                paragraph = '{{0}}{0}{{1}}'.format(paragraphs[uid])
            paragraphs[uid] = self._version_links(paragraph, version, entry, uid)
        return '\n'.join(paragraphs)

    @staticmethod
    def _version_links(paragraph, version, entry, uid):
        """
        Adds version link information to a paragraph and its cousins

        :param paragraph (str[]):
        :param index (int):
        :param entry (Page):
        :return (nothing):
        """
        links = ''
        anchor = '<span class="version-anchor" aria-hidden="true" id="{0}"></span>'.format(str(uid))
        categories = [node.name for node in entry.elders]
        cousins = entry.cousins
        for cousin, category in zip(cousins, categories):
            if version != category and cousin.name is not None:
                links += entry.hyperlink(cousin, category, fragment='#'+str(uid)) + ' '
        links = '<span class="version-links" aria-hidden="true">{0}</span>'.format(links)
        return paragraph.format(anchor, links)

    def remove_links(self, text):
        return re.sub(r'<span class="version.*?</span>', '', text)

class InternalDictionary:
    """
    Replace links with hyperlinks to other entries in the same dictionary
    """
    def add_links(self, text, entry):
        """
        Add links of the form
            '<a href="../b/blah.html#highlulani">blah</a>'
        """
        div = ' <div class="definition">'
        lang = '[2]' #language marker
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
                                            initial, link, language, word[-1])

    def remove_links(self, text):
        regex = r'<a href="(?:\w+\.html|\.\./.*?)">(.*?)</a>'
        return re.sub(regex, r'<{0}>\1</{0}>'.format('link'), text)

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
        lang = '[2]' #language marker
        wcs = '[5]' #word classes marker
        output = []
        for line in text.splitlines():
            if line.startswith(lang):
                self.language = line[len(lang):]
            elif line.startswith(wcs):
                try:
                    pos, rest = line[len(wcs):].split(div, 1)
                except ValueError:
                    pos, rest = line[len(wcs):], ''
                line = wcs + ' '.join(map(self._link, pos.split(' '))) + div + rest
            output.append(line)
        return '\n'.join(output)

    def _link(self, pos):
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
