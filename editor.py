import tkinter as Tk
import sys
import os
import json
from smeagol.editor.site_editor import SiteEditor
from smeagol.editor.dictionary_editor import DictionaryEditor

class Smeagol(Tk.Frame, object):
    def __init__(self):
        super(Smeagol, self).__init__(master=None)
        editors = [self.open_site, self.open_dictionary]
        texts = ['Site', 'Dictionary']
        for i, (editor, text) in enumerate(zip(editors, texts)):
            button = Tk.Button(command=editor, text=text, height=8, width=14)
            button.grid(column=i, row=0)
        editors = self.sites # returns a dict: {"name": "filename"}
        for i, (name, filename) in enumerate(editors.items()):
            def handler(event=None, filename=filename):
                return self.open_site(event, filename=filename)
            button = Tk.Button(command=handler, text=name, height=2, width=14)
            button.grid(column=0, row=i+1)
        editors = self.dictionaries # returns a dict: {"name": "filename"}
        for i, (name, filename) in enumerate(editors.items()):
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
        return self.get_list('site')

    @property
    def dictionaries(self):
        return self.get_list('dictionary')
    
    def get_list(self, name):
        folder = os.getenv('LOCALAPPDATA')
        inifolder = os.path.join(folder, 'Smeagol')
        inifile = os.path.join(inifolder, f'{name}.ini')
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

if __name__ == '__main__':
    Smeagol().mainloop()
