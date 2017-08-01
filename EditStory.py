import Tkinter as Tk
from Translation import *
from Smeagol import *
import os
from random import choice
from string import printable
From

class EditStory(Edit):
    def __init__(self, directory, datafile, site, markdown, master=None):
        widgets = Widgets(3, 1, 2)
        Edit.__init__(self, 'dictionary', directory, datafile, site, markdown, widgets)
        os.chdir(directory)
        self.datafile = datafile
        self.site = site
        self.markdown = markdown
        self.entry = self.site.root[0][0][0]       # first great-grandchild
        self.chapter = Chapter(self.entry, self.markdown)
        self.windows = map(lambda x: Tk.Text(self), range(3))
        self.save_button = Tk.Button(self, text='Save', command=self.save)
        self.up_button = Tk.Button(self, text=unichr(8593), command=self.previous_chapter)
        self.down_button = Tk.Button(self, text=unichr(8595), command=self.next_chapter)
        self.left_button = Tk.Button(self, text=unichr(8592), command=self.previous_paragraph)
        self.right_button = Tk.Button(self, text=unichr(8594), command=self.next_paragraph)
        self.information = Tk.StringVar()
        self.infolabel = Tk.Label(self, textvariable=self.information)
        self.grid()
        self.create_window()
        self.top = self.winfo_toplevel()
        self.top.state('zoomed')
        self.display()
        self.windows[0].focus_set()

    def create_window(self):
        self.left_button.grid(row=0, column=0)
        self.right_button.grid(row=0, column=1)
        self.up_button.grid(row=0, column=2)
        self.down_button.grid(row=0, column=3)
        self.save_button.grid(row=0, column=4, sticky=Tk.W)
        self.infolabel.grid(row=0, column=5, sticky=Tk.W)
        font = ('Californian FB', 16)
        for i, window in enumerate(self.windows):
            window.configure(height=9, width=108, wrap=Tk.WORD, font=font)
            window.bind('<KeyPress>', self.unloadinfo)
            window.bind('<Tab>', self.next_window)
            window.bind('<Control-m>', self.refresh_markdown)
            window.bind('<Control-r>', self.literal)
            window.bind('<Control-s>', self.save)
            window.bind('<Next>', self.next_paragraph)
            window.bind('<Prior>', self.previous_paragraph)
            window.bind('<Control-Next>', self.next_chapter)
            window.bind('<Control-Prior>', self.previous_chapter)
            window.bind('<Control-BackSpace>', self.backspace_word)
            window.bind('<Control-Delete>', self.delete_word)
            window.grid(row=i+1, column=4, columnspan=5)

    def next_window(self, event):
        self.windows[(self.windows.index(event.widget) + 1) % 3].focus_set()
        return 'break'

    def unloadinfo(self, event=None):
        self.information.set('')

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
    def delete_word(event=None):
        if event.widget.get(Tk.INSERT + '-1c') in ' .,;:?!':
            event.widget.delete(Tk.INSERT, Tk.INSERT + ' wordend +1c')
        elif event.widget.get(Tk.INSERT) == ' ':
            event.widget.delete(Tk.INSERT, Tk.INSERT + '+1c wordend')
        elif event.widget.get(Tk.INSERT) in '.,;:?!':
            event.widget.delete(Tk.INSERT, Tk.INSERT + '+1c')
        else:
            event.widget.delete(Tk.INSERT, Tk.INSERT + ' wordend')
        return 'break'

    @staticmethod
    def backspace_word(event=None):
        if event.widget.get(Tk.INSERT + '-1c') in '.,;:?!':
            event.widget.delete(Tk.INSERT + '-1c wordstart', Tk.INSERT)
        else:
            event.widget.delete(Tk.INSERT + '-1c wordstart -1c', Tk.INSERT)
        return 'break'

    @staticmethod
    def literal(event=None):
        event.widget.insert(Tk.INSERT, '|- -| {}')
        event.widget.mark_set(Tk.INSERT, Tk.INSERT + '-1c')
        return 'break'

    def refresh_markdown(self, event=None):
        self.markdown.refresh()
        self.information.set('Markdown Refreshed!')
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
        text = self.windows[window].get('1.0', Tk.END + '-1c')
        text = text.replace('\n', ' | ')
        return text

    def display(self):
        for window, text in zip(self.windows, self.chapter.display()):
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
        self.paragraph[3] = self.interlinear()     # Interlinear
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

    def interlinear(self):
        italic = False
        if self.paragraph[0] == '* **':
            return '&id=* **&vlinks='
        literal = self.paragraph[4][self.paragraph[4].find(' |- -| '):]
        text = '[t]&id={0}&vlinks={1} | -| &flex;'.format(self.paragraph[0], literal)
        # remove middot, and replace angle brackets with parentheses
        self.paragraph[3] = self.paragraph[2].replace('.(', '(').replace('<', '(').replace('>', ')')
        for transliteration, gloss in morpheme_split(self.paragraph[3], self.paragraph[4]):
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
