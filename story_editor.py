from editor import *
from random import choice
from string import printable


class StoryEditor(Editor):
    def __init__(self, site=None, markdown=None, links=None, master=None):
        font = ('Californian FB', 16)
        widgets = WidgetAmounts(headings=2, textboxes=4, radios='languages')
        super(StoryEditor, self).__init__(site, markdown, links, widgets, font)
        self.entry = self.root = self.site.root[0]
        self.paragraphs = self.count = self.current_paragraph = None

    def prepare_entry(self, entry):
        """
        Manipulate entry content to suit textboxes.
        Subroutine of self.load()
        Overrides parent method
        :param entry (Page): A Page instance carrying text. Other Pages relative to this entry may also be accessed.
        :param return (str[]):
        """
        prepare = super(StoryEditor, self).prepare_entry
        texts = map(lambda x: prepare(x)[0], entry.cousins)
        self.make_paragraphs(texts)
        texts = self.prepare_paragraphs(self.paragraphs[self.current_paragraph])
        return texts

    def make_paragraphs(self, texts):
        cousins = map(lambda x: x.splitlines(), texts)     # Str[][]
        self.count = max(map(len, cousins))      # int
        self.current_paragraph = min(map(len, cousins)) - 1    # int
        cousins = map(self.add_padding, cousins, len(cousins) * [self.count])     # still Str[][], but now padded
        self.paragraphs = map(None, *cousins) # str()[] (transposed)

    def add_padding(self, text, length):
            return text + (length - len(text)) * ['']

    def prepare_paragraphs(self, paragraph):
        displays = [paragraph[2 * i] for i in xrange(3)]
        displays[2:4] = displays[2].split(' |- -| ')
        if len(displays) == 3:
            displays.append('{}')
        displays[3] = displays[3][1:-1]
        replacements = [['.(', '&middot;('],
                        ['(', chr(5)],
                        ['<', 2*chr(5)],
                        [')', chr(6)],
                        ['>', 2*chr(6)],
                        ['-', chr(7)]]
        for j, i in reversed(replacements):
            displays[1] = displays[1].replace(i, j)     # Transliteration
        return displays

    def move_paragraph(self, direction=1):
        if -direction < self.current_paragraph < self.count - direction:
            self.current_paragraph += direction
            texts = self.prepare_paragraphs(self.paragraphs[self.current_paragraph])
            self.display(texts)
        self.information.set('Paragraph #' + str(self.current_paragraph))
        return 'break'

    def previous_paragraph(self, event=None):
        return self.move_paragraph(-1)

    def next_paragraph(self, event=None):
        return self.move_paragraph(1)

    @staticmethod
    def get_text(textbox):
        """
        Retrieves text from textbox and removes line-breaks.
        Overrides Editor.get_text()
        """
        return str(textbox.get(1.0, Tk.END + '-1c')).replace('\n', ' | ')

    def prepare_texts(self, texts):
        """
        Modify entry with manipulated texts.

        Overrrides parent method
        :param return (Nothing):
        :called by: self.save()
        """
        cousins = self.entry.cousins
        paragraph = self.convert_paragraph(texts)
        self.paragraphs[self.current_paragraph] = paragraph
        texts = map(join_strip, zip(*self.paragraphs))
        texts = map(self.convert_texts, texts, cousins)
        for text, cousin in zip(texts, cousins):
            cousin.content = text

    def convert_paragraph(self, texts):
        """
        Returns 5 versions of the same paragraph, based on the texts.
        :param entry (Page):
        :param texts (str[]):
        :param markdown (Markdown):
        :called by: Editor.save()
        """
        paragraphs = [None] * 5
        literal = texts.pop()
        paragraphs[0:5:2] = texts
        with conversion(self.translator, 'convert_sentence') as converter:
            paragraphs[1] = converter(paragraphs[2])    # Tinellbian
        paragraphs[4] += ' |- -| {' + literal + '}'      # Literal
        paragraphs[3] = interlinear(paragraphs, self.markdown)     # Interlinear
        punctuation = ['.(', '(', ')', '-']
        with conversion(self.markdown, 'find_formatting') as converter:
            punctuation += list(converter('small-caps'))
        replacements = ['&middot;(', chr(5), chr(6), 2*chr(5), 2*chr(6), chr(7)]
        for i, j in zip(punctuation, replacements):
            paragraphs[2] = paragraphs[2].replace(i, j)     # Transliteration
        return tuple(paragraphs)

    def publish(self, entry, site):
        """
        Put entry contents into datafile, publish appropriate Pages.
        This is the default method - other Editor programs may override this.
        Subroutine of self.save()
        :param entry (Page):
        :return (nothing):
        """
        for cousin in entry.cousins:
            cousin.publish(site.template)
        # reset entry so that it is not published twice
        super(StoryEditor, self).publish(entry=None, site=site)

    @property
    def textbox_commands(self):
        commands = super(StoryEditor, self).textbox_commands
        commands += [('<Next>', self.next_paragraph),
                     ('<Prior>', self.previous_paragraph)]
        return commands

def interlinear(paragraph, markdown):
    """
    Format text from paragraphs for an interlinear gloss.
    :param paragraph (str[]): the paragraph texts from which to build the interlinear.
        paragraph[0]: English
        paragraph[1]: (not used here)
        paragraph[2]: Full paragraph transliteration
        paragraph[3]: Transliterated Tinellbian morphemes
        paragraph[4]: Morpheme gloss
    :return (str): an interlinear in Story markdown.
    """
    if paragraph[0] == '* **':
        return '* **'
    italics = markdown.find_formatting('em')
    upright = ('', '')
    font_style = upright
    literal = paragraph[4][paragraph[4].find(' |- -| '):]
    text = '[t]{0}{1} | -| &flex;'.format(paragraph[0], literal)
    # remove middot, and replace angle brackets with parentheses
    paragraph[3] = paragraph[2].replace('.(', '(').replace('<', '(').replace('>', ')')
    for transliteration, gloss in morpheme_split(paragraph[3], paragraph[4]):
        if transliteration[0].startswith(italics[0]):
            transliteration[0] = transliteration[0][len(italics[0]):]
            font_style = italics
        text += inner_table(transliteration, gloss, font_style)
        if transliteration[-1].endswith(italics[1]):
            font_style = upright
    text += '}[/t]'
    return text


def morpheme_split(*texts):
    output = []
    for text in texts:
        output.append([word.split(r'-') for word in text.split(' ')])
    return zip(*output)


def inner_table(top, bottom, font_style):
    output = '[t]{{0}}{0}{{1}} | [r]{1} | [/t]'.format(r'{1}- | {0}'.join(top), r'- | '.join(bottom))
    output = output.format(*font_style)
    return output


def join_strip(texts):
    """
    For each string, remove linebreaks from the end, then join them
        together.

    :param texts (str()):
    :return (str):
    """
    return str(re.sub(r'\n*$', '', '\n'.join(texts), flags=re.M))


if __name__ == '__main__':
    app = StoryEditor(site=Story(),
                      markdown=Markdown('c:/users/ryan/documents/'
                            'tinellbianlanguages/storyreplacements.mkd'),
                      links=AddRemoveLinks([InternalStory()]))
    app.master.title('Story Editor')
    app.mainloop()
