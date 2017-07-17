from random import randint
import re
import datetime


class Translator:
    def __init__(self, language):
        self.language = language
        self.converter = None
        self.name = ''
        self.set_language(self.language)

    def convert_text(self, text):
        return self.converter.convert_text(text)

    def convert_word(self, text):
        return self.converter.convert_word(text)

    def convert_sentence(self, text):
        return self.converter.convert_sentence(text)

    def set_language(self, language):
        self.language = language.lower()
        if self.language == "hl":
            self.converter = HighLulani()
        elif self.language == "en":
            self.converter = English()
        else:
            raise NameError('No such language ' + language)
        self.name = self.converter.name


class English:
    def __init__(self):
        self.name = 'English'

    @staticmethod
    def convert_text(text):
        return ''

    @staticmethod
    def convert_sentence(text):
        return ''

    @staticmethod
    def convert_word(text):
        return ''


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

        # removes anything between angle brackets
        text = re.sub(r'<.*?>', '', text)

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
    def __init__(self, number):
        self.total = 0
        self.maximum = number

    def next(self):
        if self.total == self.maximum:
            self.total = 0
            raise StopIteration
        self.total += 1
        return self.word()

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
        if num and not randint(0, 10):
            return consonant + syllable if consonant != unichr(8217) else unichr(660) + vowel
        else:
            return syllable


class Markdown:
    def __init__(self, filename='c:/users/ryan/documents/tinellbianlanguages/replacements.html'):
        """
        Marking down proceeds down the Replacements page
        :param filename (String): the path to the replacements file
        """
        self.markup, self.markdown = [], []
        with open(filename) as replacements:
            for line in replacements:
                line = line.split(" ")
                self.markup.append(line[0])
                self.markdown.append(line[1])
        self.source = None
        self.destination = None

    def to_markup(self, text, datestamp=True):
        self.source, self.destination = self.markdown[::-1], self.markup[::-1]
        text += datetime.datetime.strftime(datetime.datetime.today(), '&date=%Y%m%d\n') if datestamp else ''
        return self.convert(text)

    def to_markdown(self, text, datestamp=True):
        self.source, self.destination = self.markup, self.markdown
        text = re.sub(r'&date=\d{8}\n', '', text) if datestamp else text
        return self.convert(text)

    def convert(self, text):
        for first, second in zip(self.source, self.destination):
            text = text.replace(first, second)
        return text
