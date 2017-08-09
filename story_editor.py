from default_editor import *
from random import choice
from string import printable

class EditStory(Editor):
    def __init__(self, directory, datafile, site, markdown, master=None):
        self.font = ('Californian FB', 16)
        self.widgets = WidgetAmounts(headings=2, textboxes=4, radios='languages')
        super(EditStory, self).__init__(directory, datafile, site, markdown)
        self.site = site
        self.markdown = markdown
        self.datafile = datafile
        self.entry = self.site.root[0]
        self.paragraphs = self.count = self.current_paragraph = None
        self.configure_widgets()

    def configure_widgets(self):
        for textbox in self.textboxes:
            textbox.bind('<Next>', self.next_paragraph)
            textbox.bind('<Prior>', self.previous_paragraph)
        for i, heading in enumerate(self.headings):

            def handler(event, self=self, i=i):
                return self.scroll_headings(event, i)
            heading.bind('<Prior>', handler)
            heading.bind('<Next>', handler)
        self.headings[0].bind('<Return>', self.insert_chapter)
        self.headings[0].bind('<Tab>', self.insert_chapter)
        self.headings[1].bind('<Return>', self.load)
        self.headings[1].bind('<Tab>', self.load)
        self.configure_language_radios()

    def load(self, event=None):
        """
        Find entry, manipulate entry to fit boxes, place in boxes
        Overrides parent method
        """
        super(EditStory, self).load()
        self.entry, self.paragraphs, self.current_paragraph, self.count = self.entry
        self.information.set('Paragraph #' + str(self.current_paragraph))

    def find_entry(self, headings):
        """
        Find the current entry based on what is in the heading boxes.
        Overrides parent method.
        Subroutine of self.load().
        :param headings (str[]): the texts from the heading boxes
        :return (Page, str()[], int):
        :   (Page): current entry
        :   (str()[]): a list of paragraphs, where each paragraph consists of different versions
        :   (int): the index of the last untranslated paragraph
        :   (int): the index of the last paragraph overall
        """
        entry = super(EditStory, self).find_entry([self.site.root[0].name] + headings)
        cousins = map(lambda x: x.content.splitlines(), entry.cousins)     # Str[][]
        count = max(map(len, cousins))      # int
        current_paragraph = min(map(len, cousins)) - 1    # int
        cousins = map(lambda x: x + (count - len(x)) * [''], cousins)     # still Str[][], but now padded
        paragraphs = map(None, *cousins) # str()[] (transposed)
        return entry, paragraphs, current_paragraph, count

    @staticmethod
    def prepare_entry(entry, markdown=None, kind=None):
        """
        Manipulate entry content to suit textboxes.
        Subroutine of self.load()
        Overrides parent method
        :param entry (Page): A Page instance carrying text. Other Pages relative to this entry may also be accessed.
        :param markdown (Markdown): a Markdown instance to be applied to the contents of the entry. If None, the content is not changed.
        :param return (str[]):
        """
        entry, paragraphs, current_paragraph, count = entry
        paragraph = paragraphs[current_paragraph]
        displays = map(lambda x: remove_version_links(paragraph[2 * x]), range(3))
        # have to add and subtract final '\n' because of how markdown interacts with the timestamp
        with conversion(markdown, 'to_markdown') as converter:
            displays = map(converter, displays)
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
        for j, i in replacements[::-1]:
            displays[1] = displays[1].replace(i, j)     # Transliteration
        return displays

    def scroll_headings(self, event, level):
        """
        Respond to PageUp / PageDown by changing headings, moving through the hierarchy.
        :param event (Event): which entry box received the KeyPress
        :param level (int): the level of the hierarchy that is being traversed.
        """
        if level <= 1:
            heading = self.headings[level]
            level += 2
            direction = 1 if event.keysym == 'Next' else -1
            # traverse hierarchy sideways
            if self.entry.level == level:
                with ignored(IndexError):
                    self.entry = self.entry.sister(direction)
            # ascend hierarchy until correct level
            while self.entry.level > level:
                with ignored(AttributeError):
                    self.entry = self.entry.parent
            # descend hierarchy until correct level
            while self.entry.level < level:
                with ignored(IndexError):
                    self.entry = self.entry.children[0]
            for k in range(level - 2, 2):
                self.headings[k].delete(0, Tk.END)
            heading.insert(Tk.INSERT, self.entry.name)
        else:       # scrolling the heading for the paragraph number
            if event.keysym == 'Next':
                self.next_paragraph()
            else:
                self.previous_paragraph()
        return 'break'

    def insert_chapter(self, event):
        self.headings[1].focus_set()
        return 'break'

    def insert_heading(self, event=None):
        self.headings[2].focus_set()
        return 'break'

    def previous_paragraph(self, event=None):
        return self.move_paragraph(-1)

    def next_paragraph(self, event=None):
        return self.move_paragraph(1)

    def move_paragraph(self, direction=1):
        if -direction < self.current_paragraph < self.count - direction:
            self.current_paragraph += direction
            entry = self.entry, self.paragraphs, self.current_paragraph, self.count
            self.display(self.prepare_entry(entry, self.markdown))
        self.information.set('Paragraph #' + str(self.current_paragraph))
        return 'break'

    @staticmethod
    def get_text(textbox):
        """
        Retrieves text from textbox and removes line-breaks.
        Overrides Editor.get_text()
        """
        return str(textbox.get(1.0, Tk.END + '-1c')).replace('\n', ' | ')

    @staticmethod
    def prepare_texts(entry, site, texts, markdown=None, replacelinks=None, kind=None):
        """
        Modify entry with manipulated texts.
        Subroutine of self.save().
        Overrrides parent method
        :param entry (Page): the entry in the datafile to be modified.
        :param texts (str[]): the texts to be manipulated and inserted.
        :param markdown (Markdown): a Markdown instance to be applied to the texts. If None, the texts are not changed.
        :param return (Nothing):
        """
        contents = map(join_strip, zip(*texts))
        cousins = entry.cousins
        for content, cousin in zip(contents, cousins):
            cousin.content = content

    @staticmethod
    def prepare_paragraph(entry, texts, markdown=None, translator=None, uid=None):
        """
        Returns 5 versions of the same paragraph, based on the texts.
        :param entry (Page):
        :param texts (str[]):
        :param markdown (Markdown):
        :called by: Editor.save()
        :calls (static): interlinear(), add_version_links()
        """
        length = 8
        paragraphs = [None] * 5
        literal = texts.pop()
        paragraphs[0:5:2] = texts
        with conversion(translator, 'convert_sentence') as converter:
            paragraphs[1] = converter(paragraphs[2])    # Tinellbian
        paragraphs[4] += ' |- -| {' + literal + '}'      # Literal
        paragraphs[3] = interlinear(paragraphs, markdown)     # Interlinear
        for i in range(3):
            paragraphs[i] = '&id={0}&vlinks='.format(paragraphs[i])
        with conversion(markdown, 'to_markup') as converter:
            paragraphs = map(converter, paragraphs)
        replacements = [['.(', '&middot;('],
                        ['(', chr(5)],
                        ['<small-caps>', 2*chr(5)],
                        [')', chr(6)],
                        ['</small-caps>', 2*chr(6)],
                        ['-', chr(7)]]
        for i, j in replacements:
            paragraphs[2] = paragraphs[2].replace(i, j)     # Transliteration
        paragraphs[4] = '&id=' + paragraphs[4].replace(' | [r]', '&vlinks= | [r]') # Gloss
        for index, paragraph in enumerate(paragraphs):
            paragraphs[index] = add_version_links(paragraph, index, entry, uid)
        return tuple(paragraphs)

    @staticmethod
    def publish(entry, site):
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
        super(EditStory, EditStory).publish(entry=None, site=site)


def add_version_links(paragraph, index, entry, uid):
    """
    Adds version link information to a paragraph and its cousins
    :param paragraph (str[]):
    :param index (int):
    :param entry (Page):
    :return (nothing):
    """
    links = ''
    anchor = '<span class="version-anchor" id="{0}"></span>'.format(str(uid))
    categories = [node.name for node in entry.elders]
    cousins = entry.cousins
    for i, (cousin, category) in enumerate(zip(cousins, categories)):
        if index != i:
            links += cousins[index].hyperlink(cousin, category, fragment='#'+str(uid)) + '&nbsp;'
    links = '<span class="version-links">{0}</span>'.format(links)
    return paragraph.replace('&id=', anchor).replace('&vlinks=', links)


def remove_version_links(text):
    """
    Remove the version link information from a paragraph.
    :precondition: text is in Smeagol markdown
    :param text (str): the paragraph to be cleaned.
    :return (str):
    """
    return re.sub(r'<span class="version.*?</span>', '', text)


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
    italics = markdown.find_formatting('em')
    upright = ('', '')
    font_style = upright
    if paragraph[0] == '* **':
        return '&id=* **&vlinks='
    literal = paragraph[4][paragraph[4].find(' |- -| '):]
    text = '[t]&id={0}&vlinks={1} | -| &flex;'.format(paragraph[0], literal)
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
    Join
    :param texts (str()):
    :return (str):
    """
    return str(re.sub(r'\n*$', '', '\n'.join(texts), flags=re.M))


if __name__ == '__main__':
    app = StoryEditor(directory='c:/users/ryan/documents/tinellbianlanguages/thecoelacanthquartet',
                    datafile='data.txt',
                    site=Story(),
                    markdown=Markdown('c:/users/ryan/documents/tinellbianlanguages/storyreplacements.html'))
    app.master.title('Editor the Story')
    app.mainloop()
