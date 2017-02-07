import random
import re


class Translator:
    def __init__(self, language):
        self.language = language
        if self.language == "HL":
            self.converter = HighLulani()
        else:
            raise NameError("No such language")

    def convert_text(self, text):
        return self.converter.convert_text(text)


class HighLulani:
    def __init__(self):
        pass

    # Converts a transliterated text into High Lulani text
    # See grammar.tinellb.com/highlulani for details.
    @staticmethod
    def convert_text(text):
        # removes markdown tags
        text = re.sub("\[(|/)[bik]\]", "", text)

        # replaces "upper case" glottal stop with "lower case" apostrophe
        text = re.sub("(\"| |^)''", "\\1'", text)
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
        if text == "***":
            return text
        output = "[hl]." + self.convert_text(text) + ".[/hl]"
        return output

    def convert_word(self, text):
        output = "[hl]\\(" + self.convert_text(text) + "\\)[/hl]"
        return output


def interlinear(english, transliteration, gloss):
    italic = False
    if english == "***":
        return "***\n"
    literal = gloss[gloss.find(' | [r]'):]
    text = '[t]' + english + literal + ' | [r]'
    for t_word, g_word in morpheme_split(transliteration, gloss):
        if t_word[0][:3] == '[i]':
            t_word[0] = t_word[0][3:]
            italic = True
        text += inner_table(t_word, g_word, italic)
        if t_word[-1][-4:] == '[/i]':
            italic = False
    text += '[/t]'
    print(text)
    return text


def morpheme_split(*texts):
    output = []
    for text in texts:
        output.append([word.split(r"\-") for word in text.split(" ")])
    return zip(*output)


def inner_table(top, bottom, italic=False):
    if italic:
        output = '[t][i]{0}[/i] | [r](1) | [/t]'.format(r'[/i]\- | [i]'.join(top), r'\- | '.join(bottom))
    else:
        output = '[t]{0} | [r]{1} | [/t]'.format(r'\- | '.join(top), r'\- | '.join(bottom))
    return output


def random_scaled_pick(from_list, scale):
    try:
        pick = from_list[[i <= random.randint(1, sum(scale)) for i in [sum(scale[:i])
                                                                       for i in range(len(scale))]].index(False) - 1]
    except ValueError:
        pick = from_list[-1]
    return pick


def make_word():
    consonant_scale = [10, 10, 11, 12, 13, 14, 15, 16, 17, 19, 21, 24, 27, 32, 38, 47, 62, 82]
    consonants = ['b', 'g', 'j', 'f', 'h', 'd', 'p', 'r', 't', 'm', 'c', 'x', 'q', 'n', 'k', 'l', unichr(8217), 's']
    vowel_scale = [4, 2, 1]
    vowels = ['a', 'i', 'u']
    syllable = [1, 2, 3, 4]
    syllable_scale = [7, 18, 15, 2]
    num = random_scaled_pick(syllable, syllable_scale)
    new_word = ""
    for i in range(num):
        new_word += random_scaled_pick(consonants, consonant_scale)
        if random.random() > 0.9 and i > 0:
            new_word += new_word[-1]
            if new_word[-2:] == '**':
                new_word = new_word[:-2] + unichr(660)
        new_word += random_scaled_pick(vowels, vowel_scale)
    return new_word


class Markdown:
    def __init__(self, filename='c:/users/ryan/documents/tinellbianlanguages/replacements.html'):
        self.markup = []
        self.markdown = []
        with open(filename) as replacements:
            for line in replacements:
                line = line.split(" ")
                self.markup.append(line[1])
                self.markdown.append(line[0])
        self.source = None
        self.destination = None

    def to_markup(self, text):
        while True:
            try:
                open_brace = text.index("{") + 1
                close_brace = text.index("}")
                if close_brace <= open_brace:
                    raise ValueError
            except ValueError:
                break
            link = text[open_brace:close_brace].lower()
            link = link.replace(" ", "")
            if link[:2] == "''":
                link = link[1:]
            if link[0] == "'":
                cat = link[1]
            elif link[:2] == "\\-":
                cat = link[2]
            else:
                cat = link[0]
            link = link.replace("'", "\\'")
            link = link.replace("&#x20;", "")
            link = "<a href=\\\"../" + cat + "/" + link + ".html\\\">"
            text = text[:open_brace-1] + link + text[open_brace:close_brace] + "</a>" + text[close_brace+1:]
        self.source, self.destination = self.markdown[::-1], self.markup[::-1]
        return self.convert(text)

    def to_markdown(self, text):
        while True:
            try:
                open_a = text.index("<a")
                close_a = text.index(">", open_a) + 1
            except ValueError:
                break
            text = text.replace("</a>", "}")
            text = text[:open_a] + "{" + text[close_a:]
        self.source, self.destination = self.markup, self.markdown
        return self.convert(text)

    def convert(self, text):
        for first, second in zip(self.source, self.destination):
            text = text.replace(first, second)
        return text

