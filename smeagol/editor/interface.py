import tkinter.filedialog as fd

from .. import conversion, errors, utils
from ..utilities import RandomWords
from ..defaults import default
from ..site import Site


class Interface:
    def __init__(self):
        self.new_config()

    def __getattr__(self, attr):
        if attr == 'site_info':
            return self.config['site']
        else:
            return getattr(super(), attr)
    
    def open_site(self, filename):
        if not filename:
            options = dict(filetypes=[('Sméagol File', '*.smg'), ('Source Data File', '*.src')],
                        title='Open Site',
                        defaultextension='.smg')
            filename = fd.askopenfilename(**options)
        if filename:
            self.config = self.setup(filename)
        headings = self.config.get('current', {}).get('page', [])
        return self.find_entry(headings)

    def setup(self, filename):
        if filename.endswith('.smg'):
            config = utils.load(filename)
            for key, value in config['site'].items():
                setattr(self.site, key, value)
        else:
            config = default.config
            self.site.source = filename
        self.site.refresh_tree()
        return config

    def new_config(self):
        self.translator = conversion.Translator()
        self.marker = conversion.Markdown()
        self.tagger = conversion.Tagger()
        self.linker = conversion.Linker()
        self.randomwords = RandomWords()
        self.site = Site()

    def find_entry(self, headings):
        entry = self.site.root
        for heading in headings:
            try:
                entry = entry[heading]
            except (KeyError, IndexError):
                break
        return entry
    
    def change_language(self, language):
        self.translator.select(language)
        self.randomwords.select(language)
