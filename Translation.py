import random
import re


class Translator:
    def __init__(self, language):
        self.language = language.upper()
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
        self.language = language.upper()
        if self.language == "HL":
            self.converter = HighLulani()
        elif self.language == "EN":
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


def random_scaled_pick(from_list, scale):
    try:
        pick = map(lambda x: sum(scale[:x]), range(len(scale)))
        pick = map(lambda x: x <= random.randint(1, sum(scale)), pick).index(False) - 1
        pick = from_list[pick]
    except ValueError:
        pick = from_list[-1]
    return pick


def make_word(number):
    consonant_scale = [10, 10, 11, 12, 13, 14, 15, 16, 17, 19, 21, 24, 27, 32, 38, 47, 62, 82]
    consonants = ['b', 'g', 'j', 'f', 'h', 'd', 'p', 'r', 't', 'm', 'c', 'x', 'q', 'n', 'k', 'l', unichr(8217), 's']
    vowel_scale = [4, 2, 1]
    vowels = ['a', 'i', 'u']
    syllable = [1, 2, 3, 4]
    syllable_scale = [7, 18, 15, 2]
    new_words = []
    for _ in range(number):
        num = random_scaled_pick(syllable, syllable_scale)
        new_word = ""
        for i in range(num):
            new_word += random_scaled_pick(consonants, consonant_scale)
            if random.random() > 0.9 and i > 0:
                new_word += new_word[-1]
                if new_word[-2:] == '**':
                    new_word = new_word[:-2] + unichr(660)
            new_word += random_scaled_pick(vowels, vowel_scale)
        new_words.append(new_word)
    return new_words


class Markdown:
    def __init__(self, filename='c:/users/ryan/documents/tinellbianlanguages/replacements.html'):
        """
        Marking down proceeds down the Replacements page
        :param filename:
        """
        self.markup = []
        self.markdown = []
        with open(filename) as replacements:
            for line in replacements:
                line = line.split(" ")
                self.markup.append(line[0])
                self.markdown.append(line[1])
        self.source = None
        self.destination = None

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

