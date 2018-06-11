import Tkinter as Tk
import sys
import os
import json
from cwsmeagol.editor.site_editor import SiteEditor
from cwsmeagol.editor.dictionary_editor import DictionaryEditor
from cwsmeagol.editor.translation_editor import TranslationEditor


class Smeagol(Tk.Frame, object):
    def __init__(self):
        super(Smeagol, self).__init__(master=None)
        editors = [self.open_site, self.open_dictionary]
        texts = ['Site', 'Dictionary']
        for i, (editor, text) in enumerate(zip(editors, texts)):
            button = Tk.Button(command=editor, text=text, height=8, width=14)
            button.grid(column=i, row=0)
        editors = self.sites # returns a dict: {"name": "filename"}
        for i, (name, filename) in enumerate(editors.iteritems()):
            def handler(event=None, filename=filename):
                return self.open_site(event, filename=filename)
            button = Tk.Button(command=handler, text=name, height=2, width=14)
            button.grid(column=0, row=i+1)
        editors = self.dictionaries # returns a dict: {"name": "filename"}
        for i, (name, filename) in enumerate(editors.iteritems()):
            def handler(event=None, filename=filename):
                return self.open_dictionary(event, filename=filename)
            button = Tk.Button(command=handler, text=name, height=2, width=14)
            button.grid(column=1, row=i+1)
        self.master.bind('s', self.open_site)
        self.master.bind('d', self.open_dictionary)
        if len(sys.argv) > 1:
            if sys.argv[1] in ('-s', 's', '--site'):
                self.open_site()
            elif sys.argv[1] in ('-d', 'd', '--dictionary'):
                self.open_dictionary()

    @property
    def sites(self):
        folder = os.getenv('LOCALAPPDATA')
        inifolder = os.path.join(folder, 'Smeagol')
        inifile = os.path.join(inifolder, 'site.ini')
        try:
            with open(inifile) as iniload:
                return json.load(iniload)
        except (IOError, ValueError):
            return dict()

    @property
    def dictionaries(self):
        folder = os.getenv('LOCALAPPDATA')
        inifolder = os.path.join(folder, 'Smeagol')
        inifile = os.path.join(inifolder, 'dictionary.ini')
        try:
            with open(inifile) as iniload:
                return json.load(iniload)
        except (IOError, ValueError):
            return dict()

    def open_editor(self, editor, filename=None):
        top = Tk.Toplevel()
        editor(top, filename)
        self.master.withdraw()

    def open_site(self, event=None, filename=None):
        self.open_editor(SiteEditor, filename)

    def open_dictionary(self, event=None, filename=None):
        self.open_editor(DictionaryEditor, filename)

Smeagol().mainloop()
