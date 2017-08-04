import Tkinter as Tk
from Translation import *
from Smeagol import *
from Edit import *
from random import choice
from string import printable

class EditStory(Edit):
    def __init__(self, directory, datafile, site, markdown, master=None):
        self.font = ('Californian FB', 16)
        self.widgets = [3, 3, 'languages']
        Edit.__init__(self, directory, datafile, site, markdown)
        self.site = site
        self.markdown = markdown
        self.datafile = datafile
        self.entry = self.site.root[0][0][0]       # first great-grandchild
        self.chapter = Chapter(self.entry, self.markdown)
        self.configure_widgets()

    def configure_widgets(self):
        for textbox in self.textboxes:
            textbox.bind('<Control-r>', self.literal)
            textbox.bind('<Next>', self.next_paragraph)
            textbox.bind('<Prior>', self.previous_paragraph)
            textbox.bind('<Control-Next>', self.next_chapter)
            textbox.bind('<Control-Prior>', self.previous_chapter)
        self.configure_language_radios()

    def previous_chapter(self, event=None):
        if self.entry.level > 2:
            self.entry = self.entry.parent
            self.chapter = Chapter(self.entry, self.markdown)
            self.display()
            self.information.set('')
        return 'break'

    def next_chapter(self, event=None):
        try:
            old = self.entry
            self.entry = self.entry.next_node()
            if self.entry.next_node().level <= 1:
                self.entry = old
            else:
                self.chapter = Chapter(self.entry, self.markdown)
            self.display()
            self.information.set('')
        except ValueError:
            pass
        return 'break'

    def previous_paragraph(self, event=None):
        self.chapter.previous_paragraph()
        self.display()
        self.information.set('')
        return 'break'

    def next_paragraph(self, event=None):
        self.chapter.next_paragraph()
        self.display()
        self.information.set('')
        return 'break'

    @staticmethod
    def literal(event=None):
        event.widget.insert(Tk.INSERT, '|- -| {}')
        event.widget.mark_set(Tk.INSERT, Tk.INSERT + '-1c')
        return 'break'

    def save(self, event=None):
        content = self.chapter.save(map(self.get_text, range(3)), self.entry)
        cousins = self.entry.cousins()
        for text, cousin in zip(content, cousins):
            cousin.content = text
        page = re.sub(r'\n+', '\n', str(self.site))
        if page:
            with open(self.datafile, 'w') as data:
                data.write(page)
        self.entry.publish(self.site.template)
        for cousin in cousins:
            cousin.publish(self.site.template)
        self.site.update_json()
        self.information.set('Saved!')
        return 'break'

    def get_text(self, window):
        text = self.textboxes[window].get('1.0', Tk.END + '-1c')
        text = text.replace('\n', ' | ')
        return text

    def display(self):
        for window, text in zip(self.textboxes, self.chapter.display()):
            window.delete('1.0', Tk.END)
            window.insert('1.0', text)
        return 'break'


class Chapter:
    def __init__(self, node, markdown):
        cousins = map(lambda x: x.content.splitlines(), node.cousins())     # Str[][]
        count = max(map(len, cousins)) + 1      # int
        self.current_paragraph = min(map(len, cousins)) - 1     # int
        cousins = map(lambda x: x + (count - len(x)) * [''], cousins)     # still Str[][], but now padded
        cousins = zip(*cousins)    # Str()[]
        self.paragraphs = map(lambda x: Paragraph(list(x), markdown), cousins)     # Paragraph[]

    def display(self):
        return self.paragraphs[self.current_paragraph].display()

    def save(self, texts, entry):
        """
        Cause the current paragraph to update itself
        :param texts:
        :return (nothing):
        """
        self.paragraphs[self.current_paragraph].save(texts, entry)
        return map(lambda x: str('\n'.join(x)), zip(*map(lambda x: x.paragraph, self.paragraphs)))

    def next_paragraph(self):
        try:
            self.current_paragraph += 1
            self.display()
        except IndexError:
            self.current_paragraph -= 1

    def previous_paragraph(self):
        try:
            self.current_paragraph -= 1
            self.display()
        except IndexError:
            self.current_paragraph += 1


class Paragraph:
    def __init__(self, paragraphs, markdown):
        self.markdown = markdown
        self.paragraph = paragraphs     # Str[]

    def display(self):
        markdown = self.markdown.to_markdown
        displays = map(lambda x: self.remove_version_links(self.paragraph[2 * x]), range(3))
        # have to add and subtract final '\n' because of how markdown works
        displays = map(lambda x: markdown(x + '\n').replace('\n', ''), displays)
        replacements = [['.(', '&middot;('],
                        ['(', chr(5)],
                        ['<', 2*chr(5)],
                        [')', chr(6)],
                        ['>', 2*chr(6)],
                        ['-', chr(7)]]
        for j, i in replacements[::-1]:
            displays[1] = displays[1].replace(i, j)     # Transliteration
        return displays

    @staticmethod
    def remove_version_links(text):
        """
        Remove the version link information from a paragraph.
        :param text (str): the paragraph to be cleaned.
        :return (str):
        """
        return re.sub(r'<span class="version.*?</span>', '', text)

    def save(self, texts, entry):
        """
        Update this paragraph
        :param texts:
        :return: (nothing)
        """
        markup = self.markdown.to_markup
        translate = Translator('HL').convert_sentence
        self.paragraph[0:5:2] = texts
        self.paragraph[1] = translate(self.paragraph[2])    # Tinellbian
        self.paragraph[3] = interlinear(self.paragraph)     # Interlinear
        for i in range(3):
            self.paragraph[i] = '&id={0}&vlinks='.format(self.paragraph[i])
        self.paragraph = map(markup, self.paragraph)
        replacements = [['.(', '&middot;('],
                        ['(', chr(5)],
                        ['<small-caps>', 2*chr(5)],
                        [')', chr(6)],
                        ['</small-caps>', 2*chr(6)],
                        ['-', chr(7)]]
        for i, j in replacements:
            self.paragraph[2] = self.paragraph[2].replace(i, j)     # Transliteration
        self.paragraph[4] = '&id=' + self.paragraph[4].replace(' | [r]', '&vlinks= | [r]')
        uuid = uid()
        for index, paragraph in enumerate(self.paragraph):
            self.paragraph[index] = self.add_version_links(paragraph, index, entry, uuid)

    def add_version_links(self, paragraph, index, entry, uuid):
        """
        Adds version link information to a paragraph and its cousins
        :param paragraph (Paragraph):
        :param index (int):
        :param entry (Page):
        :return (nothing):
        """
        links = ''
        anchor = '<span class="version-anchor" id="{0}"></span>'.format(uuid)
        categories = [node.name for node in entry.elders()]
        cousins = entry.cousins()
        for i, (cousin, category) in enumerate(zip(cousins, categories)):
            if index != i:
                links += cousins[index].hyperlink(cousin, category, fragment='#'+uuid) + '&nbsp;'
        links = '<span class="version-links">{0}</span>'.format(links)
        return paragraph.replace('&id=', anchor).replace('&vlinks=', links)

def interlinear(pargraph):
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
    italic = False
    if paragraph[0] == '* **':
        return '&id=* **&vlinks='
    literal = paragraph[4][paragraph[4].find(' |- -| '):]
    text = '[t]&id={0}&vlinks={1} | -| &flex;'.format(paragraph[0], literal)
    # remove middot, and replace angle brackets with parentheses
    paragraph[3] = paragraph[2].replace('.(', '(').replace('<', '(').replace('>', ')')
    for transliteration, gloss in morpheme_split(paragraph[3], paragraph[4]):
        if transliteration[0][:2] == '((':
            transliteration[0] = transliteration[0][2:]
            italic = True
        text += inner_table(transliteration, gloss, italic)
        if transliteration[-1][-2:] == '))':
            italic = False
    text += '}[/t]'
    return text

def morpheme_split(*texts):
    output = []
    for text in texts:
        output.append([word.split(r'-') for word in text.split(' ')])
    return zip(*output)


def inner_table(top, bottom, italic=False):
    if italic:
        output = '[t](({0})) | [r]{1} | [/t]'.format(r'))- | (('.join(top), r'- | '.join(bottom))
    else:
        output = '[t]{0} | [r]{1} | [/t]'.format(r'- | '.join(top), r'- | '.join(bottom))
    return output


def uid(length=8):
    """
    Creates a unique alphanumeric identification number
    :param length (int): length of the uid
    """
    return ''.join([choice(printable[:62]) for i in range(length)])


if __name__ == '__main__':
    app = EditStory(directory='c:/users/ryan/documents/tinellbianlanguages/thecoelacanthquartet',
                    datafile='data.txt',
                    site=Story(),
                    markdown=Markdown('c:/users/ryan/documents/tinellbianlanguages/storyreplacements.html'))
    app.master.title('Edit the Story')
    app.mainloop()
