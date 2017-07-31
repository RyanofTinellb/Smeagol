import Tkinter as Tk
import Translation
import os
import re
from Smeagol import *

class Edit(Tk.Frame):
    """
    Base class for EditDictionary, EditSite, TranslateStory.
    """
    def __init__(self, kind, directories, datafiles, sites, markdowns, commands, buttoninfo, labelinfo, master=None):
        """
        Initialise an instance of the Edit class.
        :param kind (str): i.e.: 'grammar', 'dictionary', 'story'.
        :param directory (str):
        :param commands ((function, str)[]): a list of tuples (command, keyboard shortcut). Each command will be bound its keyboard shortcut for each Entry and Text widget.
        """
        Tk.Frame.__init__(self, master)
        # initialise initial variables
        self.kind = kind
        self.directories = directories
        self.datafiles = datafiles
        self.sites = sites
        self.markdowns = markdowns
        self.commands = commands
        # initialise instance variables
        self.buttonframe = Tk.Frame()
        self.textframe = Tk.Frame()
        self.headings, self.radios, self.texts = [], [], []
        self.load_button = self.save_button = self.label = None
        # create window
        self.pack(expand=True, fill=Tk.BOTH)
        self.buttonframe.pack(side=Tk.LEFT)
        self.textframe.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
        # create widgets
        self.headings =
        row = 0
        for i, heading in enumerate(self.headings):
            heading.grid(row=i, column=0, colspan=2)
        row += 1 + i
        for i, button in enumerate(self.create_buttons(self.buttonframe, buttoninfo)):
            button.grid(row=row, column=i)
        row += 1
        self.create_label(self.buttonframe, labelinfo)


    def create_buttons(self, master, buttoninfo):
        return Tk.Button(master, text='Load', command=buttoninfo.load_command),
                Tk.Button(master, textvariable=buttoninfo.save_variable, command=buttoninfo.save_command)

    def create_label(self, master, labelinfo):
        return Tk.Label(master, textvariable=labelinfo.textvariable)

    def add_heading(self):
        heading = Tk.Entry(self.buttonframe)
        self.headings.append(heading)
        return heading

    def add_radio(self, text, value, command):
        variable = Tk.StringVar()
        radio = Tk.Radiobutton(self.buttonframe, text=text, value=value, variable=variable, command=command, anchor=Tk.N)
        return radio, variable

    def add_textbox(self, font='TkDefaultFont'):
        textbox = Tk.Entry(self.buttonframe, font=font, undo=True, height=1, width=1)
        return textbox


class WidgetInfo():
    def __init__(self, load_command, save_command):
        self.load_command = load_command
        self.save_command = save_command
        self.save_variable = Tk.StringVar()


class LabelInfo():
    def __init__(self):
        self.textvariable = Tk.StringVar()
