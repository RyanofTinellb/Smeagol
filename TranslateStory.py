import Tkinter as Tk
from Translation import *
from Smeagol import *


class EditStory(Tk.Frame):
    def __init__(self, master=None):
        Tk.Frame.__init__(self, master)
        self.story = Story()
        self.entry = self.story.root[0][0][0]       # first great-grandchild
        self.chapter = Chapter(self.entry)
        self.windows = map(lambda x: Tk.Text(self), range(3))
        self.publish_button = Tk.Button(self, text="Push", command=self.publish)
        self.up_button = Tk.Button(self, text=unichr(8593), command=self.previous_chapter)
        self.down_button = Tk.Button(self, text=unichr(8595), command=self.next_chapter)
        self.left_button = Tk.Button(self, text=unichr(8592), command=self.previous_paragraph)
        self.right_button = Tk.Button(self, text=unichr(8594), command=self.next_paragraph)
        self.is_bold = False
        self.is_italic = False
        self.is_small_cap = False
        self.grid()
        self.create_window()
        self.top = self.winfo_toplevel()
        self.top.state("zoomed")
        self.display()

    def create_window(self):
        self.left_button.grid(row=0, column=0)
        self.right_button.grid(row=0, column=1)
        self.up_button.grid(row=0, column=2)
        self.down_button.grid(row=0, column=3)
        self.publish_button.grid(row=0, column=4, sticky=Tk.W)
        font = ('Californian FB', 16)
        for i, window in enumerate(self.windows):
            window.configure(height=9, width=108, wrap=Tk.WORD, font=font)
            window.bind("<Control-b>", self.bold)
            window.bind("<Control-i>", self.italic)
            window.bind("<Control-k>", self.small_cap)
            window.bind("<Control-r>", self.literal)
            window.bind("<Control-s>", self.publish)
            window.bind("<Next>", self.next_paragraph)
            window.bind("<Prior>", self.previous_paragraph)
            window.bind("<Control-Next>", self.next_chapter)
            window.bind("<Control-Prior>", self.previous_chapter)
            window.bind("<Control-BackSpace>", self.delete_word)
            window.grid(row=i+1, column=4, columnspan=5)
        os.chdir('c:/users/ryan/documents/tinellbianlanguages/thecoelacanthquartet')

    def bold(self, event=None):
        if self.is_bold:
            event.widget.insert(Tk.INSERT, "[/b]")
        else:
            event.widget.insert(Tk.INSERT, "[b]")
        self.is_bold = not self.is_bold
        return "break"

    def italic(self, event=None):
        if self.is_italic:
            event.widget.insert(Tk.INSERT, "[/i]")
        else:
            event.widget.insert(Tk.INSERT, "[i]")
        self.is_italic = not self.is_italic
        return "break"

    def small_cap(self, event=None):
        if self.is_small_cap:
            event.widget.insert(Tk.INSERT, "[/k]")
        else:
            event.widget.insert(Tk.INSERT, "[k]")
        self.is_small_cap = not self.is_small_cap
        return "break"

    def previous_chapter(self, event=None):
        if self.entry.generation() > 2:
            self.entry = self.entry.parent
            self.chapter = Chapter(self.entry)
            self.display()
        return "break"

    def next_chapter(self, event=None):
        try:
            old = self.entry
            self.entry = self.entry.next_node()
            if self.entry.next_node().generation() <= 1:
                self.entry = old
            else:
                self.chapter = Chapter(self.entry)
            self.display()
        except ValueError:
            pass
        return "break"

    def previous_paragraph(self, event=None):
        self.chapter.previous_paragraph()
        self.display()
        return "break"

    def next_paragraph(self, event=None):
        self.chapter.next_paragraph()
        self.display()
        return "break"

    @staticmethod
    def delete_word(event=None):
        if event.widget.get(Tk.INSERT + "-1c") in ".,;:?!":
            event.widget.delete(Tk.INSERT + "-1c wordstart", Tk.INSERT)
        else:
            event.widget.delete(Tk.INSERT + "-1c wordstart -1c", Tk.INSERT)
        return "break"

    @staticmethod
    def literal(event=None):
        event.widget.insert(Tk.INSERT, '|- -| {}')
        event.widget.mark_set(Tk.INSERT, Tk.INSERT + '-1c')

    def publish(self, event=None):
        content = self.chapter.publish(map(self.get_text, range(3)))
        cousins = self.entry.cousins()
        for text, cousin in zip(content, cousins):
            cousin.content = text
        page = re.sub(r'\n+', '\n', str(self.story))
        if page:
            with open("data.txt", 'w') as data:
                data.write(page)
        Story().publish()
        return "break"

    def get_text(self, window):
        text = self.windows[window].get('1.0', Tk.END + '-1c')
        text = text.replace('\n', '|')
        return text

    def display(self):
        for window, text in zip(self.windows, self.chapter.display()):
            window.delete('1.0', Tk.END)
            window.insert('1.0', text)
            window.edit_modified(False)
        return "break"


class Chapter:
    def __init__(self, node):
        cousins = map(lambda x: x.content.splitlines(), node.cousins())     # Str[][]
        count = max(map(len, cousins)) + 1
        self.current_paragraph = min(map(len, cousins)) - 1
        cousins = map(lambda x: x + (count - len(x)) * [''], cousins)     # still Str[][], but now padded
        cousins = zip(*cousins)    # Str()[]
        self.paragraphs = map(lambda x: Paragraph(list(x)), cousins)     # Paragraph[]

    def display(self):
        return self.paragraphs[self.current_paragraph].display()

    def publish(self, texts):
        """
        Cause the current paragraph to update itself
        :param texts:
        :return: (nothing)
        """
        self.paragraphs[self.current_paragraph].publish(texts)
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
    def __init__(self, paragraphs):
        self.replacements = '../StoryReplacements.html'
        self.paragraph = paragraphs     # Str[]

    def display(self):
        markdown = Markdown(self.replacements).to_markdown
        displays = map(lambda x: markdown(self.paragraph[2 * x]), range(3))
        replacements = [['.(', '&middot;('],
                        ['(', chr(5)],
                        ['<', 2*chr(5)],
                        [')', chr(6)],
                        ['>', 2*chr(6)],
                        ['-', chr(7)]]
        for j, i in replacements[::-1]:
            displays[1] = display[1].replace(i, j)     # Transliteration
        return displays

    def publish(self, texts):
        """
        Update this paragraph
        :param texts:
        :return: (nothing)
        """
        markup = Markdown(self.replacements).to_markup
        translate = Translator('HL').convert_sentence
        self.paragraph[0:5:2] = texts
        self.paragraph[1] = translate(self.paragraph[2])    # Tinellbian
        self.paragraph[3] = self.interlinear()     # Interlinear
        self.paragraph = map(markup, self.paragraph)
        replacements = [['.(', '&middot;('],
                        ['(', chr(5)],
                        ['<small-caps>', 2*chr(5)],
                        [')', chr(6)],
                        ['</small-caps>', 2*chr(6)],
                        ['-', chr(7)]]
        for i, j in replacements:
            self.paragraph[2] = self.paragraph[2].replace(i, j)     # Transliteration

    def interlinear(self):
        italic = False
        if self.paragraph[0] == "* **":
            return "* **"
        literal = self.paragraph[4][self.paragraph[4].find(' |- -| '):]
        text = '[t]' + self.paragraph[0] + literal + ' | -| &flex;'
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
        output.append([word.split(r"-") for word in text.split(" ")])
    return zip(*output)


def inner_table(top, bottom, italic=False):
    if italic:
        output = '[t](({0})) | [r]{1} | [/t]'.format(r'))- | (('.join(top), r'- | '.join(bottom))
    else:
        output = '[t]{0} | [r]{1} | [/t]'.format(r'- | '.join(top), r'- | '.join(bottom))
    return output


if __name__ == '__main__':
    app = EditStory()
    app.master.title('Story Edit')
    app.mainloop()
