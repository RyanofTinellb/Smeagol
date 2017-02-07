import Tkinter as Tk
import Translator
import os
import threading
from HtmlPage import *


class EditDictionary(Tk.Frame):
    def __init__(self, master=None):
        Tk.Frame.__init__(self, master)
        self.heading = None
        self.go_button = None
        self.publish_button = None
        self.edit_text = None
        self.random_words = None
        self.random_word = Tk.StringVar()
        self.old_page = ""
        self.entry = ""
        self.new_page = ""
        self.is_bold = False
        self.is_italic = False
        self.is_small_caps = False
        self.markdown = Translator.Markdown()
        self.row_number = 0
        self.grid()
        self.top = self.winfo_toplevel()
        self.top.state("zoomed")
        self.create_widgets()
        os.chdir("C:/Users/Ryan/Documents/TinellbianLanguages/dictionary")

    def create_widgets(self):
        self.heading = Tk.Text(self, height=1, width=20, wrap=Tk.NONE)
        self.heading.grid(sticky=Tk.NE)
        self.heading.bind("<Control-r>", self.refresh_random)
        self.heading.bind("<Control-n>", self.locate_next)
        self.heading.bind("<Return>", self.bring_entry)
        self.go_button = Tk.Button(self, text="GO!", command=self.bring_entry)
        self.go_button.grid(row=1, column=1, sticky=Tk.NW)
        self.publish_button = Tk.Button(text="Publish", command=self.save)
        self.publish_button.grid(row=1, column=2, sticky=Tk.NW)
        self.random_words = Tk.Label(self, textvariable=self.random_word)
        self.random_words.grid(row=1, column=0)
        self.edit_text = Tk.Text(self, height=27, width=88, font=('Courier New', '15'))
        self.edit_text.bind("<Control-a>", self.select_all)
        self.edit_text.bind("<Control-b>", self.bold)
        self.edit_text.bind("<Control-f>", self.collapse_table)
        self.edit_text.bind("<Control-i>", self.italic)
        self.edit_text.bind("<Control-k>", self.small_caps)
        self.edit_text.bind("<Control-n>", self.new_word)
        self.edit_text.bind("<Control-r>", self.refresh_random)
        self.edit_text.bind("<Control-s>", self.save)
        self.edit_text.bind("<Control-t>", self.add_high_lulani)
        self.edit_text.bind("<Control-z>", self.bring_entry)
        self.edit_text.bind("<Control-=>", self.add_definition)
        self.edit_text.bind("<Alt-d>", self.go_to_heading)
        self.edit_text.grid(row=1, rowspan=19, column=1)
        self.heading.focus_set()

    def select_all(self, event=None):
        self.edit_text.tag_add('sel', '1.0', 'end')
        return "break"

    def locate_next(self, event=None):
        with open("new.txt", "r") as f:
            for _ in range(self.row_number):
                __ = f.readline()
            self.row_number = (self.row_number + 1) % 5
            line = f.readline()
        line = line[2:-3]
        line = line.replace('"', "'")
        line = line.split("', '")
        self.heading.delete(1.0, Tk.END)
        self.heading.insert(1.0, line[0])
        self.bring_entry()
        self.heading.delete(1.0, Tk.END)
        self.heading.insert(1.0, line[1])
        return "break"

    def go_to_heading(self, event=None):
        self.heading.focus_set()
        self.heading.tag_add('sel', '1.0', 'end-1c')
        return "break"

    def new_word(self, event=None):
        new_template = "[2]" + self.entry + "\n"
        new_template += "[3]High Lulani\n"
        new_template += "[4]" + Translator.convert_word(self.entry) + "\n"
        new_template += "[5]<ipa>//</ipa>\n"
        new_template += "[6]\n"
        self.edit_text.insert(1.0, new_template)
        self.edit_text.mark_set(Tk.INSERT, "4.9")
        self.save()
        return "break"

    def add_definition(self, event=None):
        self.edit_text.insert(Tk.INSERT, "<div ==></div>")
        self.edit_text.mark_set(Tk.INSERT, Tk.INSERT + "-6c")
        return "break"

    def refresh_random(self, event=None):
        text = "\n".join([Translator.make_word() for i in range(10)])
        self.random_word.set(text)

    def bold(self, event):
        if not self.is_bold:
            self.edit_text.insert(Tk.INSERT, "[b]")
            self.is_bold = True
        else:
            self.edit_text.insert(Tk.INSERT, "[/b]")
            self.is_bold = False
        return "break"
    
    def italic(self, event):
        if not self.is_italic:
            self.edit_text.insert(Tk.INSERT, "[i]")
            self.is_italic = True
        else:
            self.edit_text.insert(Tk.INSERT, "[/i]")
            self.is_italic = False
        return "break"
            
    def small_caps(self, event):
        if not self.is_small_caps:
            self.edit_text.insert(Tk.INSERT, "[k]")
            self.is_small_caps = True
        else:
            self.edit_text.insert(Tk.INSERT, "[/k]")
            self.is_small_caps = False
        return "break"

    def add_high_lulani(self, event):
        enter = False
        try:
            text = self.edit_text.get(Tk.SEL_FIRST, Tk.SEL_LAST)
        except Tk.TclError:
            return "break"
        if self.edit_text.compare(Tk.SEL_LAST, "==", Tk.SEL_LAST + " lineend"):
            enter = True
        if text[:4] == "href":
            start = text.find("href")
            end = text.find(">")
            text = text[end+1:]
        while "<" in text:
            start = text.find("<")
            end = text.find(">")
            if end == -1:
                break
            text = text[:start] + text[end + 1:]
        if "." in text:
            period = True
        else:
            period = False
        text = text.replace("[b]", "")
        text = text.replace("[/b]", "")
        text = text.replace("</a>", "")
        text = Translator.convert_line(text)
        if period:
            text = "." + text + "."
        text = "[hl]\\(" + text + "\\)[/hl]"
        text += "\n" if enter else " "
        self.edit_text.insert(Tk.SEL_LAST + "+1c", text)
        self.edit_text.mark_set(Tk.INSERT, Tk.INSERT + "+" + str(len(text) + 1) + "c")
        return "break"

    def collapse_table(self, event):
        text = self.edit_text.get(Tk.SEL_FIRST, Tk.SEL_LAST)
        text = text.replace("\n", " | ")
        text = text.replace(" | [r]", "\n[r]")
        self.edit_text.delete(Tk.SEL_FIRST, Tk.SEL_LAST)
        self.edit_text.insert(Tk.INSERT, text)
        return "break"

    def remove_hyperlinks(self, event):
        text = self.edit_text.get(Tk.INSERT + " linestart", Tk.INSERT + " lineend")
        self.edit_text.delete(Tk.INSERT + " linestart", Tk.INSERT + " lineend")
        text = text.replace("</a>", "")
        while True:
            start = text.find("<a ")
            if start == -1:
                break
            end = text.find(">", start)
            text = text[:start] + text[end+1:]
        self.edit_text.insert(Tk.INSERT, text)

    def bring_entry(self, event=None):
        self.markdown = Translator.Markdown()
        self.entry = self.heading.get(1.0, Tk.END + "-1c")
        self.old_page = Translator.find_entry("data.txt", self.entry)
        self.new_page = self.markdown.to_markdown(self.old_page)
        self.edit_text.delete(1.0, Tk.END)
        self.edit_text.insert(1.0, self.new_page)
        self.edit_text.focus_set()
        self.edit_text.mark_set(Tk.INSERT, "1.0")
        return "break"

    def save(self, event=None):
        if not self.old_page:
            return "break"
        self.is_bold = self.is_italic = self.is_small_caps = False
        location = self.edit_text.index(Tk.INSERT)
        self.new_page = self.edit_text.get(1.0, Tk.END)
        while self.new_page[-2:] == "\n\n":
            self.new_page = self.new_page[:-1]
        self.new_page = self.markdown.to_markup(self.new_page)
        with open("data.txt", "r") as dictionary:
            page = dictionary.read()
        page = page.replace(self.old_page, self.new_page)
        with open("data.txt", "w") as dictionary:
            dictionary.write(page)
        self.bring_entry()
        self.edit_text.mark_set(Tk.INSERT, location)
        t = threading.Thread(target=self.publish)
        t.start()
        return "break"

    @staticmethod
    def publish():
        HtmlPage("dictionary", 2)

app = EditDictionary()
app.master.title('Dictionary Edit')
app.mainloop()
