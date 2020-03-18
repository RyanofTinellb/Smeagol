import tkinter.filedialog as fd

from .. import conversion, errors, utils
from ..utilities import RandomWords
from ..defaults import default
from ..site import Site


class Interface:
    def __init__(self, filename=''):
        if filename:
            self.setup(filename)
        else:
            self.new_config()

    def __getattr__(self, attr):
        if attr == 'site_info':
            return self.config['site']
        elif attr == 'filename':
            return None
        else:
            try:
                return getattr(super(), attr)
            except AttributeError:
                name = self.__class__.__name__
                raise AttributeError(f"'{name}' object has no attribute '{attr}'")
    
    def __setattr__(self, attr, value):
        if attr == 'markdown' and isinstance(value, conversion.Markdown):
            self.config['markdown'] = value.filename
        elif attr == 'tagger' and isinstance(value, conversion.Tagger):
            self.config['styles'] = value.values
        super().__setattr__(attr, value)

    def open_site(self, filename=''):
        if not filename:
            options = dict(filetypes=[('Sméagol File', '*.smg'), ('Source Data File', '*.src')],
                           title='Open Site',
                           defaultextension='.smg')
            filename = fd.askopenfilename(**options)
        if filename:
            self.config = self.setup(filename)
        headings = self.config.get('current', {}).get('page', [])
        self.filename = filename
        return self.find_entry(headings)

    def save_site(self, filename=''):
        filename = filename or self.filename
        if filename:
            utils.save(self.config, filename)
        else:
            self.save_site_as(filename)
        self.filename = filename

    def save_site_as(self, filename=''):
        filename = filename or self.filename
        if not filename:
            options = dict(filetypes=[('Sméagol File', '*.smg')],
                           title='Save Site',
                           defaultextension='.smg')
            filename = fd.asksaveasfilename(**options)
        if filename:
            self.save_site(filename)

    def setup(self, filename):
        if filename.endswith('.smg'):
            config = utils.load(filename)
            for key, value in config['site'].items():
                setattr(self.site, key, value)
        else:
            config = default.config
            self.site.source = filename
        self.markdown.load(config.get('markdown', None))
        self.tagger.load(config.get('styles', None))
        self.site.refresh_tree()
        return config

    def new_config(self):
        self.config = default.config
        self.translator = conversion.Translator()
        self.markdown = conversion.Markdown()
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

    def display(self, entry):
        text = str(entry)
        text = self.markdown.to_markdown(text)
        text = self.tagger.hide_tags(text)
        return text
