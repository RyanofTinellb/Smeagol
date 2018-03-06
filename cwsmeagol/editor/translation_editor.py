from editor import *
from random import choice
from string import printable
from cwsmeagol.translation import Interlinear


class TranslationEditor(Editor):
    def __init__(self, properties=None, widgets=None, font=None, master=None):
        font = ('Californian FB', 16)
        widgets = WidgetAmounts(headings=2, textboxes=4, radios='languages')
        super(TranslationEditor, self).__init__(properties, widgets, font, master)
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
        prepare = super(TranslationEditor, self).prepare_entry
        texts = map(lambda x: prepare(x)[0], entry.cousins)
        self.make_paragraphs(texts)
        texts = self.prepare_paragraphs(self.paragraphs[self.current_paragraph])
        return texts

    def make_paragraphs(self, texts):
        if texts:
            cousins = map(lambda x: x.splitlines(), texts)     # Str[][]
            self.count = max(map(len, cousins))      # int
            self.current_paragraph = abs(min(map(len, cousins)) - 1)    # int >= 0
            cousins = map(self.add_padding, cousins, len(cousins) * [self.count])     # still Str[][], but now padded
            self.paragraphs = map(None, *cousins) # str()[] (transposed)
        else:
            self.count = 0
            self.current_paragraph = 0
            self.paragraphs = [('',), ('',)]

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
        texts = map(self.join_strip, zip(*self.paragraphs))
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
        paragraphs[4] += ' |- -| {' + literal + '}'      # Gloss
        paragraphs[3] = Interlinear(paragraphs, self.markdown)     # Interlinear
        punctuation = ['.(', '(', ')', '-', '<', '>']
        replacements = ['&middot;(', chr(5), chr(6), chr(7), 2*chr(5), 2*chr(6)]
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
            if cousin.name is not None:
                cousin.publish(site.template)
        # reset entry so that it is not published twice
        super(TranslationEditor, self).publish(entry=None, site=site)

    @staticmethod
    def join_strip(texts):
        """
        For each string, remove linebreaks from the end, then join them
            together.

        :param texts (str()):
        :return (str):
        """
        texts = map(str, texts)
        # flags=re.M for multiline
        return str(re.sub(r'\n*$', '', '\n'.join(texts), flags=re.M))

    @property
    def textbox_commands(self):
        commands = super(TranslationEditor, self).textbox_commands
        commands += [('<Next>', self.next_paragraph),
                     ('<Prior>', self.previous_paragraph)]
        return commands


if __name__ == '__main__':
    app = TranslationEditor(site=Story(),
                      markdown=Markdown('c:/users/ryan/documents/'
                            'tinellbianlanguages/storyreplacements.mkd'),
                      links=AddRemoveLinks([InternalStory()]))
    app.master.title('Story Editor')
    app.mainloop()
