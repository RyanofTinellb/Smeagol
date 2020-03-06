from .. import conversion
from ..site import Site

class Interface:
    def __init__(self, filename=None):
        if filename:
            self.open_config(filename)
        else:
            self.new_config()
    
    def open_config(self, filename):
        pass

    def new_config(self):
        self.translator = conversion.Translator()
        self.marker = conversion.Markdown()
        self.tagger = conversion.Tagger()
        self.linker = conversion.Linker()
        self.site = Site()
    
    def find_entry(self, headings):
        entry = self.site.root
        for heading in headings:
            entry = entry[heading]
        return entry