import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
from tkinter.font import Font

from smeagol.utilities.errors import MarkdownFileNotFound


class Markdown(tk.Frame):
    def __init__(self, parent=None, markdown=None):
        super().__init__(parent)
        self.parent.title('Editing Markdown')
        markdown = markdown
        self.original = markdown
        self.markdown = markdown.copy()
        self.font = Font(family="Calibri", size=14)
        self.position = 0
        rows, columns = 15, 2
        self.total = rows * columns
        self.frames = []
        self.grid()
        for column in range(columns):
            for row in range(rows):
                frame = EntryFrame(self, self.font)
                frame.grid(row=row, column=2*column+1, sticky='w')
                self.frames.append(frame)
            tk.Label(self, padx=10).grid(row=0, column=2*column)
        tk.Label(self, padx=10).grid(row=0, column=2*columns)
        self.buttons_frame(self).grid(row=rows, column=columns+1, sticky='e')
        self.move()

    @property
    def parent(self):
        return self.master

    def buttons_frame(self, parent=None):
        frame = tk.Frame(parent)
        tk.Button(frame, text='Load', command=self.load).grid(row=0, column=0)
        tk.Button(frame, text='Save', command=self.save).grid(row=0, column=1)
        tk.Button(frame, text='Save As', command=self.saveas).grid(
            row=0, column=2)
        tk.Button(frame, text='Cancel', command=self.cancel).grid(
            row=0, column=3)
        tk.Button(frame, text='OK', command=self.enter).grid(row=0, column=4)
        return frame

    def move(self, position=None):
        if position is not None:
            self.position = position
        for index, frame in enumerate(self.frames, start=self.position):
            while True:
                try:
                    frame.open_entry(self.markdown[index])
                    break
                except IndexError:
                    self.markdown += dict(markup='',
                                          markdown='', display_markdown=True)

    def up(self, event=None):
        self.move(max(self.position - self.total, 0))

    def down(self, event=None):
        self.move(min(self.position + self.total, 100))

    def shift(self, event=None):
        (self.down if event.delta < 0 else self.up)()

    def load(self):
        filename = fd.askopenfilename(
            filetypes=[('Sméagol Markdown File', '*.mkd')],
            title='Load Markdown',
            defaultextension='.mkd')
        try:
            self.markdown.load(filename)
            self.move(0)
        except MarkdownFileNotFound:
            self.file_not_found(filename)

    def save(self):
        try:
            self.markdown.save()
        except MarkdownFileNotFound:
            self.saveas()

    def saveas(self):
        filename = fd.asksaveasfilename(
            filetypes=[('Sméagol Markdown File', '*.mkd')],
            title='Save Markdown',
            defaultextension='.mkd')
        try:
            self.markdown.save(filename)
        except MarkdownFileNotFound:
            self.file_not_found(filename)

    def file_not_found(self, filename):
        mb.showerror('Markdown File Not Found', f'Unable to find {filename}')

    def cancel(self):
        self.markdown = self.original
        self.enter()

    def enter(self):
        self.parent.destroy()


class Entry(tk.Entry):
    def __init__(self, master, parent, name):
        super().__init__(master, font=parent.font, width=20)
        self.bind('<Prior>', parent.up)
        self.bind('<Next>', parent.down)
        self.bind('<MouseWheel>', parent.shift)

        def handler(*args, parent=parent, name=name):
            parent.entry[name] = self.get()

        self.bind('<KeyRelease>', handler)

    def set(self, text):
        self.delete(0, 'end')
        self.insert('insert', text)


class EntryFrame(tk.Frame):
    def __init__(self, parent, font):
        super().__init__(parent)
        self.display_markdown = tk.BooleanVar()
        self.state = tk.StringVar()
        self.markup = Entry(self, self.parent, 'markup')
        self.markdown = Entry(self, self.parent, 'markdown')
        self.markup.grid(row=0, column=0)
        self.markdown.grid(row=0, column=2)
        tk.Checkbutton(self, indicatoron=False, textvariable=self.state,
                       variable=self.display_markdown, command=self.set_state,
                       onvalue=0, offvalue=1, font=font, width=2).grid(row=0, column=1)

    def set_state(self, *args):
        value = bool(self.display_markdown.get())
        self.state.set('🡒' if value else '⇌')
        self.entry['display_markdown'] = value

    def open_entry(self, entry):
        self.entry = entry
        self.markup.set(entry['markup'])
        self.markdown.set(entry['markdown'])
        self.display_markdown.set(1 if entry['display_markdown'] else 0)
        self.set_state()
