from ..conversion import Markdown
import tkinter as Tk
from tkinter.font import Font


class MarkdownWindow(Tk.Frame):
    def __init__(self, master=None, markdown=None):
        super().__init__(master)
        self.master.title('Editing Markdown')
        markdown = markdown or Markdown()
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
            Tk.Label(self, padx=10).grid(row=0, column=2*column)
        Tk.Label(self, padx=10).grid(row=0, column=2*columns)
        self.buttons_frame(self).grid(row=rows, column=columns+1, sticky='e')
        self.move()

    def buttons_frame(self, master=None):
        frame = Tk.Frame(master)
        Tk.Button(frame, text='Load', command=self.load).grid(row=0, column=0)
        Tk.Button(frame, text='Save', command=self.save).grid(row=0, column=1)
        Tk.Button(frame, text='Cancel', command=self.cancel).grid(
            row=0, column=2)
        Tk.Button(frame, text='OK', command=self.enter).grid(row=0, column=3)
        return frame

    def move(self):
        print(self.position)
        for index, frame in enumerate(self.frames, start=self.position):
            while True:
                try:
                    frame.open_entry(self.markdown[index])
                    break
                except IndexError:
                    self.markdown += dict(markup='', markdown='', display_markdown=True)

    def up(self, event=None):
        self.position = max(self.position - self.total, 0)
        self.move()

    def down(self, event=None):
        self.position = min(self.position + self.total, 100)
        self.move()

    def shift(self, event=None):
        (self.down if event.delta < 0 else self.up)()

    def load(self):
        pass

    def save(self):
        pass

    def cancel(self):
        self.markdown = self.original
        self.enter()

    def enter(self):
        self.master.destroy()
    

class Entry(Tk.Entry):
    def __init__(self, master, parent):
        super().__init__(master, font=parent.font, width=20)
        self.bind('<Prior>', parent.up)
        self.bind('<Next>', parent.down)
        self.bind('<MouseWheel>', parent.shift)

    def set(self, text):
        self.delete(0, 'end')
        self.insert('insert', text)


class EntryFrame(Tk.Frame):
    def __init__(self, master, font):
        super().__init__(master)
        self.display_markdown = Tk.BooleanVar()
        self.state = Tk.StringVar()
        self.markup = Entry(self, self.master)
        self.markdown = Entry(self, self.master)
        self.markup.grid(row=0, column=0)
        self.markdown.grid(row=0, column=2)
        Tk.Checkbutton(self, indicatoron=False, textvariable=self.state,
                       variable=self.display_markdown, command=self.set_state,
                       onvalue=0, offvalue=1, font=font, width=2).grid(row=0, column=1)

    def set_state(self, *args):
        self.state.set('🡒' if self.display_markdown.get() else '⇌')
    
    def open_entry(self, entry):
        self.markup.set(entry['markup'])
        self.markdown.set(entry['markdown'])
        self.display_markdown.set(1 if entry['display_markdown'] else 0)
        self.set_state()
