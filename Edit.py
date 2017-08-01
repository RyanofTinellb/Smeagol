import Tkinter as Tk
import Translation
import os
import re
from Smeagol import *

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
        self.buttonframe = Tk.Frame(self)
        self.textframe = Tk.Frame(self)
        self.headings, self.radios, self.texts = [], [], []
        self.load_button = self.save_button = self.label = None
        self.save_text = Tk.StringVar()
        self.save_text.set('Save')
        # open correct directory
        try:
            os.chdir(self.choose(kind, directories))
        except TypeError:
            pass
        self.datafile = self.choose(kind, datafiles)
        self.site = self.choose(kind, sites)
        self.markdown = self.choose(kind, markdowns)
        # create widgets and window
        self.headings = self.create_headings(self.buttonframe, widgets.number_of_headings)
        self.radios = self.create_radios(self.buttonframe, widgets.number_of_radios)
        self.blanklabel = Tk.Label(self.buttonframe, height=1000) # enough height to push all other widgets to the top of the window.
        self.infolabel = self.create_label(self.buttonframe)
        self.buttons = self.create_buttons(self.buttonframe)
        self.buttons[1].configure(textvariable=self.save_text)
        commands = self.textbox_commands()
        self.textboxes = self.create_textboxes(self.textframe, widgets.number_of_textboxes, commands)
        self.create_window()
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
        row += 1
        for radio in self.radios:
            radio.grid(row=row, column=0, columnspan=2)
            row += 1
        for textbox in self.textboxes:
            textbox.pack(side=Tk.TOP, expand=True, fill=Tk.BOTH)
            row += 1
        self.infolabel.grid(row=row, column=0, columnspan=2)
        self.blanklabel.grid(row=row+1, column=0, columnspan=2)

    def textbox_commands(self):
        return [
        ('<Control-b>', self.bold),
        ('<Control-i>', self.italic),
        ('<Control-k>', self.small_caps),
        ('<Tab>', self.next_window),
        ('<Shift-Tab>', self.previous_window),
        ('<KeyPress-|>', self.insert_pipe)]

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
        return Tk.Label(master)

    @staticmethod
    def create_radios(master, number):
        radios = []
        for _ in range(number):
            radio = Tk.Radiobutton(master)
            radios.append(radio)
        return radios

    @staticmethod
    def create_textboxes(master, number, commands=None):
        if not commands:
            commands = []
        textboxes = []
        for _ in range(number):
            textbox = Tk.Text(master, height=1, width=1, wrap=Tk.WORD, undo=True)
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
        self.insert_characters(event, *self.find_formatting('strong'))
        return 'break'

    def italic(self, event=None):
        """
        Insert markdown for italic tags, and place insertion point between them.
        """
        self.insert_characters(event, *self.find_formatting('em'))
        return 'break'

    def small_caps(self, event=None):
        """
        Insert markdown for small-caps tags, and place insertion point between them.
        """
        self.insert_characters(event, *self.find_formatting('small-caps'))
        return 'break'

    def insert_pipe(self, event=None):
        self.insert_characters(event, ' | ')
        return 'break'

    def find_formatting(self, keyword):
        """
        Find markdown for specific formatting.
        :param keyword (str): the formatting type, in html, e.g.: strong, em, &c, &c.
        :return (tuple): the opening and closing tags, in markdown, e.g.: ([[, ]]), (<<, >>)
        """
        if self.markdown:
            start = self.markdown.markdown[self.markdown.markup.index('<' + keyword + '>')]
            end = self.markdown.markdown[self.markdown.markup.index('</' + keyword + '>')]
            return start, end
        else:
            return '', ''

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

    def next_window(self, event):
        try:
            self.textboxes[(self.textboxes.index(event.widget) + 1)].focus_set()
        except IndexError:
            self.textboxes[0].focus_set()
        return 'break'

    def previous_window(self, event):
        try:
            self.textboxes[(self.textboxes.index(event.widget) - 1)].focus_set()
        except IndexError:
            self.textboxes[-1].focus_set()

    @staticmethod
    def manipulate_entry_for_textbox(text):
        return text

    def manipulate_entry_for_datafile(text):
        return text


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
    app = Edit(widgets=widgets)
    app.mainloop()
