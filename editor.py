import Tkinter as Tk
import sys
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
        self.master.bind('s', self.open_site)
        self.master.bind('d', self.open_dictionary)
        if len(sys.argv) > 1:
            if sys.argv[1] in ('-s', 's', '--site'):
                self.open_site()
            elif sys.argv[1] in ('-d', 'd', '--dictionary'):
                self.open_dictionary()

    def open_editor(self, editor):
        top = Tk.Toplevel()
        editor(top)
        self.master.withdraw()

    def open_site(self, event=None):
        self.open_editor(SiteEditor)

    def open_dictionary(self, event=None):
        self.open_editor(DictionaryEditor)

Smeagol().mainloop()
