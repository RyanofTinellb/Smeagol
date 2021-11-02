import tkinter as Tk
from tkinter import simpledialog as sd
from tkinter import ttk

from ..conversion import api as conversion
from ..utilities import errors
from ..utilities import filesystem as fs
from ..utilities import utils
from . import api as wd
from ..editor.interface.interfaces import Interfaces


class Manager(Tk.Frame):
    '''Manages widgets for Editor'''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = self.master