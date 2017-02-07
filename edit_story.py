import Tkinter as Tk
import sys
import os
import Translator
import threading
from HtmlPage import HtmlPage


class EditStory(Tk.Frame):
    def __init__(self, master=None):
        Tk.Frame.__init__(self, master)
        self.chapter = None
        self.paragraph = None
        self.english = Tk.Text(self)
        self.transliteration = Tk.Text(self)
        self.gloss = Tk.Text(self)
        self.windows = [[self.english, 1], [self.transliteration, 3], [self.gloss, 5]]
        self.publish_button = Tk.Button(self, text="Push", command=self.publish)
        self.up_button = Tk.Button(self, text=unichr(8593), command=self.previous_chapter)
        self.down_button = Tk.Button(self, text=unichr(8595), command=self.next_chapter)
        self.left_button = Tk.Button(self, text=unichr(8592), command=self.previous_paragraph)
        self.right_button = Tk.Button(self, text=unichr(8594), command=self.next_paragraph)
        self.is_bold = False
        self.is_italic = False
        self.is_small_cap = False
        self.english_stars = "<span class=\\\"centre\\\">*&nbsp;&nbsp;&nbsp;&nbsp;*&nbsp;&nbsp;&nbsp;&nbsp;*</span>"
        self.tinellbian_stars = "<span class=\\\"centre\\\"><high-lulani>.</high-lulani>&nbsp;&nbsp;&nbsp;&nbsp;" \
                                "<high-lulani>.</high-lulani>&nbsp;&nbsp;&nbsp;&nbsp;<high-lulani>.</high-lulani>" \
                                "</span>"
        self.page = ""
        self.story = []
        self.markdown = Translator.Markdown()
        self.grid()
        self.create_window()
        self.top = self.winfo_toplevel()
        self.top.state("zoomed")
        self.open_file()

    def create_window(self):
        self.left_button.grid(row=0, column=0)
        self.right_button.grid(row=0, column=1)
        self.up_button.grid(row=0, column=2)
        self.down_button.grid(row=0, column=3)
        self.publish_button.grid(row=0, column=4, sticky=Tk.W)
        font = ('Calibri', 16)
        for window, i in self.windows:
            window.configure(height=7, width=108, wrap=Tk.WORD, font=font)
            window.bind("<Control-b>", self.bold)
            window.bind("<Control-i>", self.italic)
            window.bind("<Control-k>", self.small_cap)
            window.bind("<Control-s>", self.publish)
            window.bind("<Control-r>", self.literal)
            window.bind("<Next>", self.next_paragraph)
            window.bind("<Prior>", self.previous_paragraph)
            window.bind("<Control-Next>", self.next_chapter)
            window.bind("<Control-Prior>", self.previous_chapter)
            window.bind("<KeyPress-minus>", self.insert_hyphen)
            window.bind("<Control-minus>", self.insert_ordinary_hyphen)
            window.grid(row=i, column=4, columnspan=5)

    @staticmethod
    def literal(event=None):
        event.widget.insert(Tk.INSERT, " | [r]<div ===></div>")
        event.widget.mark_set(Tk.INSERT, Tk.INSERT + "-6c")
        return "break"

    @staticmethod
    def insert_hyphen(event=None):
        event.widget.insert(Tk.INSERT, "\-")
        return "break"

    @staticmethod
    def insert_ordinary_hyphen(event=None):
        event.widget.insert(Tk.INSERT, "-")
        return "break"

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

    def open_file(self):
        os.chdir("c:/users/ryan/documents/tinellbianLanguages/story")
        with open("data.txt") as story:
            self.page = story.read()
        self.initialise()

    def initialise(self):
        self.page = self.markdown.to_markdown(self.page)
        self.story = self.page.split('[1]')
        for i, section in enumerate(self.story):
            self.story[i] = section.split('[3]')
            for j, chapter in enumerate(self.story[i]):
                count = self.story[i][j].count("\n") - self.story[1][j].count("\n")
                self.story[i][j] = (chapter + count * "\n").split('\n')
        if self.chapter is None:
            self.chapter = len(self.story[1]) - 1
            self.paragraph = self.story[5][self.chapter].index("") - 1
        self.refresh()

    def refresh(self):
        try:
            self.story[3][self.chapter][self.paragraph] = \
                self.story[3][self.chapter][self.paragraph].replace(chr(7), "\-")
        except IndexError:
            pass
        if self.story[1][self.chapter][self.paragraph] == self.english_stars:
            for textbox, index in self.windows:
                textbox.delete(1.0, Tk.END)
                textbox.insert(1.0, "***")
        else:
            for textbox, index in self.windows:
                textbox.delete(1.0, Tk.END)
                try:
                    textbox.insert(1.0, self.story[index][self.chapter][self.paragraph])
                except IndexError:
                    pass
        
    def next_paragraph(self, event=None):
        self.paragraph += 1
        self.refresh()
        return "break"
        
    def previous_paragraph(self, event=None):
        if self.paragraph > 0:
            self.paragraph -= 1
            self.refresh()
        return "break"

    def next_chapter(self, event=None):
        self.chapter += 1
        self.paragraph = 1
        self.refresh()
        return "break"

    def previous_chapter(self, event=None):
        if self.chapter > 0:
            self.chapter -= 1
            self.paragraph = 1
            self.refresh()
        return "break"

    def publish(self, event=None):
        for window, i in self.windows:
            box_text = window.get(1.0, Tk.END).replace("\n", "")
            self.story[i][self.chapter][self.paragraph] = box_text
        english, transliteration, gloss = [self.story[i][self.chapter][self.paragraph] for i in [1, 3, 5]]
        if english == "***":
            for i in range(1, 6):
                if i == 2:
                    self.story[i][self.chapter][self.paragraph] = self.tinellbian_stars
                else:
                    self.story[i][self.chapter][self.paragraph] = self.english_stars
        else:
            self.story[4][self.chapter][self.paragraph] = Translator.interlinear(english, transliteration, gloss)
            self.story[2][self.chapter][self.paragraph] = Translator.convert_sentence(transliteration.replace("\-", ""))
        for i, section in enumerate(self.story):
            for j, chapter in enumerate(section):
                self.story[i][j] = "\n".join(chapter)
        for i, section in enumerate(self.story):
            self.story[i] = "[3]".join(section)
        self.story[3] = self.story[3].replace("\-", chr(7))
        self.page = "[1]".join(self.story)
        while True:
            self.page = self.page.replace("\n\n", "\n")
            if self.page.count("\n\n") == 0:
                break
        self.page = self.markdown.to_markup(self.page)
        with open("data.txt", "w") as story:
            story.write(self.page)
        t = threading.Thread(target=self.write_file)
        t.start()
        if event:
            box = event.widget
        else:
            box = self.english
        cursor = box.index(Tk.INSERT)
        self.initialise()
        box.focus_set()
        box.mark_set(Tk.INSERT, cursor)
        box.see(Tk.INSERT)
        return "break"

    @staticmethod
    def write_file():
        HtmlPage("story", 3)

app = EditStory()
app.master.title('Story Edit')
app.mainloop()
