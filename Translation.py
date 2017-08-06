import re
import datetime
from collections import OrderedDict as Odict
from random import randint
from contextlib import contextmanager

@contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass

@contextmanager
def converter(AttributeError):
    try:
        yield
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


class Markdown:
    def __init__(self, filename):
        """
        Marking down proceeds down the Replacements page
        :param filename (String): the path to the replacements file
        :raise IOError: filename does not exist
        """
        self.filename = filename
        self.markup, self.markdown = [], []
        self.source = None
        self.destination = None
        with open(filename) as replacements:
            for line in replacements:
                line = line.split(" ")
                self.markup.append(line[0])
                self.markdown.append(line[1])

    def to_markup(self, text, datestamp=True):
        self.source, self.destination = self.markdown[::-1], self.markup[::-1]
        text += datetime.datetime.strftime(datetime.datetime.today(), '&date=%Y%m%d\n') if datestamp else ''
        return self.convert(text)

    def to_markdown(self, text, datestamp=False):
        self.source, self.destination = self.markup, self.markdown
        text = re.sub(r'&date=\d{8}\n', '', text) if not datestamp else text
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
            return self.markdown[self.markup.index(text)]
        except ValueError:
            return ''

    def refresh(self):
        self.markup, self.markdown = [], []
        self.source = None
        self.destination = None
        with open(self.filename) as replacements:
            for line in replacements:
                line = line.split(" ")
                self.markup.append(line[0])
                self.markdown.append(line[1])

class d2gReplace():
    """
    Replace given words in parts of speech with URLs.
    :param filename (str): filename to get replacements from.
    """
    def __init__(self, filename):
        self.languages, self.words, self.urls = [], [], []
        with open(filename) as replacements:
            replacements = replacements.read()
        for line in replacements.splitlines():
            if line.startswith('#'):
                language = line[1:]
            else:
                word, url = line.split()
                self.languages.append(language)
                self.words.append(word)
                self.urls.append('http://grammar.tinellb.com/' + url)

    def replace(self, text):
        """
        Replaces appropriate words with links in text.
        :precondition: text is a dictionary entry in Dictionary markdown.
        """
        for language, word, url in zip(self.languages, self.words, self.urls):
            page = ''
            url = r'\\<a href=\\"{0}\\"\\>{1}\\</a\\>'.format(url, word)
            for line in text.splitlines():
                if line.startswith('[3]'):
                    current_language = line[len('[3]'):]
                elif word in line and url not in line and current_language == language:
                    line = re.sub(r'(\[6\].*?)\b' + word + r'\b(.*?{{)', r'\1' + url + r'\2', line)
                page += line + '\n'
            text = page
        return text
