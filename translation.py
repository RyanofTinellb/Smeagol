import re
from datetime import datetime
from collections import OrderedDict as Odict
from random import randint
from contextlib import contextmanager
from urllib import quote


@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass

@contextmanager
def conversion(converter, function):
    """
    Ensures a converter exists.
    Returns identity function if not.
    :param converter (object):
    :param function (str):
    """
    try:
        yield getattr(converter, function)
    except AttributeError:
        yield lambda x: x


class Translator:
    def __init__(self, language=None):
        languages = Odict()
        languages['en'] = English
        languages['hl'] = HighLulani
        self.languages = languages
        try:
            language = language.lower()
            self.converter = languages[language]()
        except (IndexError, AttributeError):
            self.converter = English()
        self.name = self.converter.name
        self.code = language
        self.number = len(languages)

    def convert_text(self, text):
        return self.converter.convert_text(text)

    def convert_word(self, text):
        return self.converter.convert_word(text)

    def convert_sentence(self, text):
        return self.converter.convert_sentence(text)


class English:
    def __init__(self):
        self.name = 'English'

    @staticmethod
    def convert_text(text):
        return text

    @staticmethod
    def convert_sentence(text):
        return text

    @staticmethod
    def convert_word(text):
        return text


class HighLulani:
    def __init__(self):
        self.name = 'High Lulani'

    # Converts a transliterated text into High Lulani text
    # See grammar.tinellb.com/highlulani for details.
    @staticmethod
    def convert_text(text):
        if text == '* **':
            return text

        # removes full stops if before a parenthesis
        text = text.replace('.(', '(')

        # removes markdown tags, hyphens, dollars, parentheses and quote marks
        text = re.sub("\[(|/)[bik]\]|-|[$()]|'\\\"|\\\"", "", text)

        # removes angle brackets
        text = re.sub(r'[<>]', '', text)

        # replaces "upper case" glottal stop with "lower case" apostrophe
        text = re.sub("(\"| |^)''", r"\1'", text)
        text = text.lower()
        output = ""
        for last, this in zip(text, text[1:]):
            if this == last:
                output += ";"
            elif last == "-":
                if this in "aiu":
                    output += "/" + this
            elif last == "'":
                output += this
            elif this == "a":
                output += last
            elif this == "i":
                output += last.upper()
            elif this == "u":
                index = "pbtdcjkgmnqlrfsxh".find(last)
                output += "oOeEyY><UIAWwvzZV"[index]
            elif this == " ":
                if last in ".!?":
                    output += " . "
                elif last in ",;:":
                    output += " , "
                else:
                    output += " / "
        output = output.replace("<", "&lt;")
        output = output.replace(">", "&gt;")
        output = output.replace("-", "")
        return output

    def convert_sentence(self, text):
        if text == '* **':
            return '[hl]* **[/hl]'.format(text)
        output = '[hl].{0}.[/hl]'.format(self.convert_text(text))
        return output

    def convert_word(self, text):
        output = r'[hl]\({0}\)[/hl]'.format(self.convert_text(text))
        return output


class RandomWords():
    def __init__(self, number, geminate):
        self.maximum = number
        self.geminate = geminate

    def words(self):
        return [self.word() for x in range(self.maximum)]

    def __iter__(self):
        return self

    def consonant(self):
        lst = ['b', 'g', 'j', 'f', 'h', 'd', 'p', 'r', 't', 'm', 'c', 'x', 'q', 'n', 'k', 'l', unichr(8217), 's']
        scale = [10, 10, 11, 12, 13, 14, 15, 16, 17, 19, 21, 24, 27, 32, 38, 47, 62, 82]
        return self.pick(lst, scale)

    def vowel(self):
        lst = ['a', 'i', 'u']
        scale = [4, 2, 1]
        return self.pick(lst, scale)

    def numsyllables(self):
        lst = [1, 2, 3, 4]
        scale = [7, 18, 15, 2]
        return self.pick(lst, scale)

    @staticmethod
    def pick(lst, scale):
        try:
            output = map(lambda x: sum(scale[:x]), range(len(scale)))
            output = map(lambda x: x <= randint(1, sum(scale)), output).index(False) - 1
            output = lst[output]
        except ValueError:
            output = lst[-1]
        return output

    def syllable(self):
        return self.consonant() + self.vowel()

    def word(self):
        return ''.join([self.double(self.syllable(), i) for i in range(self.numsyllables())])

    def double(self, syllable, num):
        consonant, vowel = list(syllable)
        if num and not randint(0, self.geminate):
            return consonant + syllable if consonant != unichr(8217) else unichr(660) + vowel
        else:
            return syllable


def urlform(text, markdown=None):
    name = text.lower()
    safe_punctuation = '\'.$_+!()'
    # remove safe punctuations that should only be used to encode non-ascii characters
    name = re.sub(r'[{0}]'.format(safe_punctuation), '', name)
    with conversion(markdown, 'to_markdown') as converter:
        name = converter(name)
    # remove extraneous initial apostrophes
    name = re.sub(r"^''+", "'", name)
    # remove text within tags
    name = re.sub(r'<(div|ipa).*?\1>', '', name)
    # remove tags, spaces and punctuation
    name = re.sub(r'<.*?>|[/*;: ]', '', name)
    name = quote(name, safe_punctuation)
    return name


class Markdown:
    def __init__(self, filename):
        """
        Marking down proceeds down the Replacements page
        :param filename (String): the path to the replacements file
        :raise IOError: filename does not exist
        """
        self.markup, self.markdown = [], []
        self.source = None
        self.destination = None
        try:
            with open(filename) as replacements:
                for line in replacements:
                    line = line.split(" ")
                    self.markup.append(line[0])
                    self.markdown.append(line[1])
                self.filename = filename
        except IOError:
            self.filename = ''

    def to_markup(self, text):
        self.source, self.destination = self.markdown[::-1], self.markup[::-1]
        return self.convert(text)

    def to_markdown(self, text):
        self.source, self.destination = self.markup, self.markdown
        return self.convert(text)

    def convert(self, text):
        for first, second in zip(self.source, self.destination):
            text = text.replace(first, second)
        return text

    def find_formatting(self, keyword):
        """
        Find markdown for specific formatting.
        :param keyword (str): the formatting type, in html, e.g.: strong, em, &c, &c.
        :return (tuple): the opening and closing tags, in markdown, e.g.: ([[, ]]), (<<, >>)
        """
        start = self.find('<' + keyword + '>')
        if start == '':
            start = self.find('<' + keyword)
        end = self.find('</' + keyword + '>')
        return start, end

    def find(self, text):
        """
        Find markdown for particular formatting.
        :param text (str):
        """
        try:
            return self.to_markdown(text)
        except ValueError:
            return ''

    def refresh(self):
        self.markup, self.markdown = [], []
        self.source = None
        self.destination = None
        if filename:
            with open(self.filename) as replacements:
                for line in replacements:
                    line = line.split(" ")
                    self.markup.append(line[0])
                    self.markdown.append(line[1])

def add_datestamp(text):
    text += datetime.strftime(datetime.today(), '&date=%Y%m%d')
    return text

def remove_datestamp(text):
    return re.sub(r'&date=\d{8}', '', text)

def replace_datestamp(text):
    return add_datestamp(remove_datestamp(text))


class AddRemoveLinks:
    def __init__(self, link_adders):
        """
        Allow for the removal of all links, and addition of specific
            links to Smeagol pages

        :param link_adders: (obj[]) a list of link adder instances
        """
        self.link_adders = link_adders
        self.details = dict(map(self.get_details, link_adders))

    @staticmethod
    def get_details(adder):
        adder_name = adder.name
        try:
            adder_filename = adder.filename
        except AttributeError:
            adder_filename = ''
        return (adder_name, adder_filename)

    def add_links(self, text, entry, site):
        for link_adder in self.link_adders:
            text = link_adder.add_links(text, entry, site)
        return text

    def remove_links(self, text):
        # external links to the dictionary - leaves as links
        text = re.sub('<a href="http://dictionary.tinellb.com/.*?">(.*?)</a>', r'<link>\1</link>', text)
        # version links - removes entire span
        text = re.sub(r'<span class="version.*?</span>', '', text)
        # internal links
        text = re.sub(r'<a href=\"(?!http).*?\">(.*?)</a>', r'<link>\1</link>', text)
        # protect phonology links from subsequent line
        text = re.sub(r'<a( href=\"http://grammar.*?phonology.*?</a>)', r'<b\1', text)
        # external links to the grammar guide, except phonology
        text = re.sub(r'<a href=\"http://grammar.*?\">(.*?)</a>', r'\1', text)
        # un-protect phonology
        text = re.sub(r'<b( href=\"http://grammar.*?phonology.*?</a>)', r'<a\1', text)
        return text

class ExternalDictionary:
    def add_links(self, text, entry, site):
        """
        Replaces text of the form <link>Blah</link> with a hyperlink to the
            dictionary entry 'Blah' on the Tinellbian languages dictionary site.
        """
        links = set(re.sub(r'.*?<link>(.*?)</link>.*?', r'\1@', text.replace('\n', '')).split(r'@')[:-1])
        language = urlform(entry.ancestors[1].name)
        for link in links:
            url = urlform(link, site.markdown)
            initial = re.sub(r'.*?(\w).*', r'\1', url)
            with ignored(KeyError):
                text = text.replace('<link>' + link + '</link>',
                '<a href="http://dictionary.tinellb.com/' + initial + '/' + url + '.html#' + language + '">' + link + '</a>')
        return text

    @property
    def name(self):
        return 'externaldictionary'

class InternalStory:
    def add_links(self, text, entry, site):
        """
        Add version links to the each paragraph of the text

        :param entry: (Page)
        :param text: (str)
        :return: (str)
        """
        paragraphs = text.splitlines()
        version = entry.elders.index(entry.ancestors[1])
        for uid, paragraph in enumerate(paragraphs[1:], start=1):
            if paragraph == '<span class="stars">*&nbsp;&nbsp;&nbsp;&nbsp;*&nbsp;&nbsp;&nbsp;&nbsp;*</span>':
                pass
            elif version == 4:
                 paragraph = '&id=' + paragraphs[uid].replace(' | [r]', '&vlinks= | [r]')
            elif version == 3:
                paragraph = '[t]&id=' + re.sub(r'(?= \| \[r\]<div class=\"literal\">)', '&vlinks=', paragraphs[uid][3:])
            else:
                paragraph = '&id=' + paragraphs[uid] + '&vlinks='
            paragraphs[uid] = self._version_links(paragraph, version, entry, uid)
        return '\n'.join(paragraphs)

    @staticmethod
    def _version_links(paragraph, index, entry, uid):
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
        for i, (cousin, category) in enumerate(zip(cousins, categories)):
            if index != i:
                links += cousins[index].hyperlink(cousin, category, fragment='#'+str(uid)) + '&nbsp;'
        links = '<span class="version-links" aria-hidden="true">{0}</span>'.format(links)
        return paragraph.replace('&id=', anchor).replace('&vlinks=', links)

    @property
    def name(self):
        return 'internalstory'

class InternalDictionary:
    """
    Replace particular words in parts of speech with links to grammar.tinellb.com
    """
    def add_links(self, text, entry, site):
        links = set(re.sub(r'.*?<link>(.*?)</link>.*?', r'\1>', text.replace('\n', '')).split(r'>')[:-1])
        for link in links:
            with ignored(KeyError):
                lower_link = re.sub(r'^&#x294;', r'&rsquo;', link).lower()
                text = text.replace('<link>' + link + '</link>', entry.hyperlink(site[lower_link], link))
        return text

    @property
    def name(self):
        return 'internaldictionary'

class ExternalGrammar:
    """
    Replace given words in parts of speech with external URLs.
    :param filename (str): filename to get replacements from.
    """
    def __init__(self, filename):
        self.languages, self.words, self.urls = [], [], []
        self.filename = filename
        with open(filename) as replacements:
            replacements = replacements.read()
        for line in replacements.splitlines():
            if line.startswith('&'):
                site = line[1:]
            elif line.startswith('#'):
                language = line[1:]
                site += urlform(language)
            else:
                word, url = line.split()
                self.languages.append(language)
                self.words.append(word)
                self.urls.append(site + url)

    def add_links(self, text, entry, site):
        """
        Add links to text, from
        :precondition: text is a dictionary entry in Smeagol markdown.
        """
        current_language = ''
        for language, word, url in zip(self.languages, self.words, self.urls):
            page = ''
            url = r'<a href="{0}">{1}</a>'.format(url, word)
            for line in text.splitlines():
                if line.startswith('[3]'):
                    current_language = line[len('[3]'):]
                elif word in line and url not in line and current_language == language:
                    line = re.sub(r'(\[6\].*?)\b' + word + r'\b(.*?<)', r'\1' + url + r'\2', line)
                page += line + '\n'
            text = page
        return text

    @property
    def name(self):
        return 'externalgrammar'
