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
        # create widgets
        self.headings = self.create_headings(self.buttonframe, widgets.number_of_headings)
        self.radios = self.create_radios(self.buttonframe, widgets.number_of_radios)
        self.blanklabel = Tk.Label(self.buttonframe, height=1000) # enough height to push all other widgets to the top of the window.
        self.infolabel = self.create_label(self.buttonframe)
        self.buttons = self.create_buttons(self.buttonframe)
        self.textboxes = self.create_textboxes(self.textframe, widgets.number_of_textboxes)
        self.create_window()
        self.top = self.winfo_toplevel()
        self.top.state('zoomed')

    def create_window(self):
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

    @staticmethod
    def create_headings(master, number):
        headings = []
        for _ in range(number):
            heading = Tk.Entry(master)
            headings.append(heading)
        return headings

    @staticmethod
    def create_buttons(master):
        return [Tk.Button(master), Tk.Button(master)]

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
    def create_textboxes(master, number):
        textboxes = []
        for _ in range(number):
            textbox = Tk.Text(master, height=1, width=1)
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
