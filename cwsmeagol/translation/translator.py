import re
from collections import OrderedDict

class Translator:
    def __init__(self, language=None):
        languages = OrderedDict()
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
