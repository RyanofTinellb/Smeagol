

class Interlinear:
    def __init__(self, paragraphs, markdown):
        """
        Format text from paragraphs for an interlinear gloss.
        :param paragraph (str[]): the paragraph texts from which to build the interlinear.
            paragraphs[0]: English
            paragraphs[1]: (not used here)
            paragraphs[2]: Full paragraph transliteration
            paragraphs[3]: Transliterated Tinellbian morphemes
            paragraphs[4]: Morpheme gloss
        :return (str): an interlinear in Story markdown.
        """
        if paragraphs[0] == '* **':
            return '* **'
        italics = markdown.find_formatting('em')
        upright = ('', '')
        font_style = upright
        literal = paragraphs[4][paragraphs[4].find(' |- -| '):]
        text = '[t]{0}{1} | -| &flex;'.format(paragraphs[0], literal)
        # remove middot, and replace angle brackets with parentheses
        paragraphs[3] = paragraphs[2].replace('.(', '(').replace('<', '(').replace('>', ')')
        for transliteration, gloss in self.morpheme_split(paragraphs[3], paragraphs[4]):
            if transliteration[0].startswith(italics[0]):
                transliteration[0] = transliteration[0][len(italics[0]):]
                font_style = italics
            text += self.inner_table(transliteration, gloss, font_style)
            if transliteration[-1].endswith(italics[1]):
                font_style = upright
        text += '}[/t]'
        self.text = text

    def __str__(self):
        return self.text

    @staticmethod
    def morpheme_split(*texts):
        output = []
        for text in texts:
            output.append([word.split(r'-') for word in text.split(' ')])
        return zip(*output)

    @staticmethod
    def inner_table(top, bottom, font_style):
        output = '[t]{{0}}{0}{{1}} | [r]{1} | [/t]'.format(r'{1}- | {0}'.join(top), r'- | '.join(bottom))
        output = output.format(*font_style)
        return output
