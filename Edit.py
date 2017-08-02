from Smeagol import *
from Translation import *
import Tkinter as Tk
import os
import re

class Edit(Tk.Frame):
    """
    Base class for EditDictionary, EditSite, TranslateStory.
    """
    def __init__(self, kind=None, directories=None, datafiles=None, sites=None, markdowns=None, widgets=None):
        """
        Initialise an instance of the Edit class.
        :param kind (str): i.e.: 'grammar', 'dictionary', 'story'.
        :param directory (str):
        """
        Tk.Frame.__init__(self, None)
        # initialise initial variables
        self.kind = kind
        self.directories = directories
        self.datafiles = datafiles
        self.sites = sites
        self.markdowns = markdowns

        # initialise instance variables
        self.buttonframe, self.textframe = Tk.Frame(self), Tk.Frame(self)
        self.headings, self.radios, self.texts = [], [], []
        self.buttons = self.load_button = self.save_button = self.label = None
        self.save_text, self.language = Tk.StringVar(), Tk.StringVar()
        self.save_text.set('Save')
        self.translator = Translator()

        # create widgets and window
        try:
            widgets = self.widgets
        except AttributeError:
            self.widgets = widgets  # check if widgets were passed as an initial argument
            if widgets is None:
                widgets = self.widgets = Widgets(0, 0, 0)
        self.headings = self.create_headings(self.buttonframe, widgets.number_of_headings)
        if widgets.number_of_radios == 'languages':
            widgets.number_of_radios = self.translator.number
        self.radios = self.create_radios(self.buttonframe, widgets.number_of_radios)
        self.blanklabel = Tk.Label(self.buttonframe, height=1000) # enough height to push all other widgets to the top of the window.
        self.infolabel, self.information = self.create_label(self.buttonframe)
        self.buttons = self.create_buttons(self.buttonframe)
        self.load_button, self.save_button = self.buttons
        self.save_button.configure(textvariable=self.save_text)
        commands = self.textbox_commands()
        while True:
            try:
                self.textboxes = self.create_textboxes(self.textframe, widgets.number_of_textboxes, commands, self.font)
                break
            except AttributeError:  # font missing
                self.font = ('Calibri', 17)
        self.create_window()

        # open site
        self.opensite(self.kind)

        # prepare window to begin
        self.top = self.winfo_toplevel()
        self.top.state('zoomed')

    def create_window(self):
        """
        Place all widgets in GUI window.
        Stack the textboxes on the right-hand side, taking as much room as possible.
        Stack the heading boxes, the buttons, radiobuttons and a label in the top-left corner.
        """
        self.pack(expand=True, fill=Tk.BOTH)
        self.buttonframe.pack(side=Tk.LEFT)
        self.textframe.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
        row = 0
        for heading in self.headings:
            heading.grid(row=row, column=0, columnspan=2, sticky=Tk.N)
            row += 1
        for i, button in enumerate(self.buttons):
            button.grid(row=row, column=i)
        row += 1
        for radio in self.radios:
            radio.grid(row=row, column=0, columnspan=2)
            row += 1
        for textbox in self.textboxes:
            textbox.pack(side=Tk.TOP, expand=True, fill=Tk.BOTH)
            row += 1
        self.infolabel.grid(row=row, column=0, columnspan=2)
        self.blanklabel.grid(row=row+1, column=0, columnspan=2)

    def opensite(self, kind):
        try:
            os.chdir(self.choose(kind, self.directories))
        except TypeError:   # if self.directories is None, remain in initial directory
            pass
        self.site = self.choose(kind, self.sites)
        self.markdown = self.choose(kind, self.markdowns)
        for heading in self.headings:
            heading.delete(0, Tk.END)
        for textbox in self.textboxes:
            textbox.delete(1.0, Tk.END)
        self.information.set('')
        try:
            self.headings[0].focus_set()
        except IndexError:  # no headings
            pass

    def textbox_commands(self):
        return [
        ('<KeyPress>', self.edit_text_changed),
        ('<Control-a>', self.select_all),
        ('<Control-b>', self.bold),
        ('<Control-i>', self.italic),
        ('<Control-k>', self.small_caps),
        ('<Control-m>', self.refresh_markdown),
        ('<Control-BackSpace>', self.backspace_word),
        ('<Control-Delete>', self.delete_word),
        ('<Alt-d>', self.go_to_heading),
        ('<Tab>', self.next_window),
        ('<Shift-Tab>', self.previous_window),
        ('<KeyPress-|>', self.insert_pipe)]

    def configure_language_radios(self):
        for radio, (code, language) in zip(self.radios, self.translator.languages.items()):
            radio.configure(text=language().name, variable=self.language, value=code, command=self.change_language)
        self.language.set(self.translator.languages.keys()[0])

    def change_language(self, event=None):
        """
        Change the entry language to whatever is in the StringVar 'self.language'
        """
        self.translator = Translator(self.language.get())
        return 'break'

    @staticmethod
    def select_all(event):
        event.widget.tag_add('sel', '1.0', 'end')
        return 'break'

    def go_to_heading(self, event=None):
        """
        Move focus to the heading textbox, and select all the text therein
        """
        heading = self.headings[0]
        heading.focus_set()
        heading.select_range(0, Tk.END)
        return 'break'

    @staticmethod
    def create_headings(master, number, commands=None):
        if not commands:
            commands = []
        headings = []
        for _ in range(number):
            heading = Tk.Entry(master)
            for (key, command) in commands:
                heading.bind(key, command)
            headings.append(heading)
        return headings

    @staticmethod
    def create_buttons(master):
        return [Tk.Button(master, text='Load'), Tk.Button(master)]

    @staticmethod
    def create_label(master):
        textvariable = Tk.StringVar()
        return Tk.Label(master, textvariable=textvariable), textvariable

    @staticmethod
    def create_radios(master, number):
        radios = []
        for _ in range(number):
            radio = Tk.Radiobutton(master)
            radios.append(radio)
        return radios

    @staticmethod
    def create_textboxes(master, number, commands=None, font=None):
        if not commands:
            commands = []
        if not font:
            font = ('Courier New', '15')
        textboxes = []
        for _ in range(number):
            textbox = Tk.Text(master, height=1, width=1, wrap=Tk.WORD, undo=True, font=font)
            for (key, command) in commands:
                textbox.bind(key, command)
            textboxes.append(textbox)
        return textboxes

    @staticmethod
    def change_directory(directory):
        os.chdir(directory)

    @staticmethod
    def choose(kind, variables):
        """
        Return appropriate variable from a dictionary, or returns the variable itself if its not a dictionary.
        :param kind (str): which variable to return.
        :param variables (Object{,}): a dictionary of {kind, variable} pairs.
        :param variables (Object): a single variable.
        """
        try:
            return variables[kind]
        except (TypeError, AttributeError, ValueError, KeyError):
            return variables

    def insert_characters(self, event, before, after=''):
        """
        Insert given text into a Text textbox, either around an insertion cursor or selected text, and move the cursor to the appropriate place.
        :param textbox (Tkinter Text): The Text into which the given text is to be inserted.
        :param before (str): The text to be inserted before the insertion counter, or before the selected text.
        :param after (str): The text to be inserted after the insertion cursor, or after the selected text.
        """
        textbox = event.widget
        try:
            text = textbox.get(Tk.SEL_FIRST, Tk.SEL_LAST)
            textbox.delete(Tk.SEL_FIRST, Tk.SEL_LAST)
            textbox.insert(Tk.INSERT, before + text + after)
        except Tk.TclError:
            textbox.insert(Tk.INSERT, before + after)
            textbox.mark_set(Tk.INSERT, Tk.INSERT + '-{0}c'.format(len(after)))

    def bold(self, event=None):
        """
        Insert markdown for bold tags, and place insertion point between them.
        """
        self.insert_characters(event, *self.markdown.find_formatting('strong'))
        return 'break'

    def italic(self, event=None):
        """
        Insert markdown for italic tags, and place insertion point between them.
        """
        self.insert_characters(event, *self.markdown.find_formatting('em'))
        return 'break'

    def small_caps(self, event=None):
        """
        Insert markdown for small-caps tags, and place insertion point between them.
        """
        self.insert_characters(event, *self.markdown.find_formatting('small-caps'))
        return 'break'

    def insert_pipe(self, event=None):
        self.insert_characters(event, ' | ')
        return 'break'

    @staticmethod
    def delete_word(event=None):
        widget = event.widget
        get = widget.get
        delete = widget.delete
        if get(Tk.INSERT + '-1c') in ' .,;:?!\n' or widget.compare(Tk.INSERT, '==', '1.0'):
            delete(Tk.INSERT, Tk.INSERT + ' wordend +1c')
        elif get(Tk.INSERT) == ' ':
            delete(Tk.INSERT, Tk.INSERT + '+1c wordend')
        elif get(Tk.INSERT) in '.,;:?!':
            delete(Tk.INSERT, Tk.INSERT + '+1c')
        else:
            delete(Tk.INSERT, Tk.INSERT + ' wordend')
        self.update_wordcount(event)
        return 'break'

    @staticmethod
    def backspace_word(event=None):
        widget = event.widget
        get = widget.get
        delete = widget.delete
        if get(Tk.INSERT + '-1c') in '.,;:?! ':
            delete(Tk.INSERT + '-2c wordstart', Tk.INSERT)
        elif get(Tk.INSERT) in ' ':
            delete(Tk.INSERT + '-1c wordstart -1c', Tk.INSERT)
        else:
            delete(Tk.INSERT + '-1c wordstart', Tk.INSERT)
        self.update_wordcount(event)
        return 'break'

    def load(self):
        """
        Find entry, manipulate entry to fit box, place in box.
        """
        text = manipulate_entry_for_textbox(self.entry.content)
        self.edit_text.delete(1.0, Tk.END)
        self.edit_text.insert(1.0, text)

    def save(self):
        """
        Take text from box, manipulate to fit datafile, put in datafile, publish self, update json.
        """
        text = self.edit_text.get(1.0, Tk.END + '-1c')
        self.entry.content = manipulate_entry_for_datafile(text)

    def edit_text_changed(self, event=None):
        """
        Notify the user that the edittext has been changed.
        Activates after each keypress.
        Deactivates after a save or a load action.
        """
        self.update_wordcount(event)
        if event.widget.edit_modified():
            self.save_text.set('*Save')

    def update_wordcount(self, event=None, widget=None):
        if event is not None:
            widget = event.widget
        text = widget.get(1.0, Tk.END)
        self.information.set(str(text.count(' ') + text.count('\n') - text.count('|')))

    def next_window(self, event):
        try:
            textbox = self.textboxes[(self.textboxes.index(event.widget) + 1)]
        except IndexError:
            textbox = self.textboxes[0]
        textbox.focus_set()
        self.update_wordcount(widget=textbox)
        return 'break'

    def previous_window(self, event):
        try:
            textbox = self.textboxes[(self.textboxes.index(event.widget) - 1)]
        except IndexError:
            textbox = self.textboxes[-1]
        textbox.focus_set()
        self.update_wordcount(widget=textbox)
        return 'break'

    @staticmethod
    def manipulate_entry_for_textbox(text):
        return text

    @staticmethod
    def manipulate_entry_for_datafile(text):
        return text

    def refresh_markdown(self, event=None):
        try:
            self.markdown.refresh()
            self.information.set('Markdown Refreshed!')
        except AttributeError:
            self.information.set('No Markdown Found')
        return 'break'

class Widgets():
    def __init__(self, number_of_headings=0, number_of_textboxes=0, number_of_radios=0):
        """
        :param number_of_headings (int):
        :param number_of_textboxes (int):
        :param radio_names (str[]):
        """
        self.number_of_headings = number_of_headings
        self.number_of_textboxes = number_of_textboxes
        self.number_of_radios = number_of_radios


if __name__ == '__main__':
    widgets = Widgets(3, 3,  3)
    app = Edit()
    app.mainloop()
