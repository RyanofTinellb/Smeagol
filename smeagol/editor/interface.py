import tkinter.filedialog as fd

from .. import conversion, errors, utils
from ..utilities import RandomWords
from ..defaults import default
from ..site import Site


class Interface:
    def __init__(self, filename=''):
        self.filename = filename
        config = self.load_config(filename) if filename else default.config
        self.setup(config)

    def __getattr__(self, attr):
        if attr == 'site_info':
            return self.config.setdefault('site', {})
        elif attr == 'tabs':
            return self.config.setdefault('tabs', [[]])
        else:
            try:
                return getattr(super(), attr)
            except AttributeError:
                name = self.__class__.__name__
                raise AttributeError(
                    f"'{name}' object has no attribute '{attr}'")

    def __setattr__(self, attr, value):
        if attr == 'markdown' and isinstance(value, conversion.Markdown):
            self.config['markdown'] = value.filename
        elif attr == 'tagger' and isinstance(value, conversion.Tagger):
            self.config['styles'] = dict(value.items())
        super().__setattr__(attr, value)
    
    @property
    def entries(self):
        return map(self.find_entry, self.tabs)

    def load_config(self, filename):
        if filename.endswith('.smg'):
            config = utils.load(filename)
        else:
            config = default.config
            config['site']['files']['source'] = filename
        return config
    
    def setup(self, config):
        self.config = config
        self.site = Site(**config.get('site', None))
        self.translator = conversion.Translator()
        self.markdown = conversion.Markdown(config.get('markdown', None))
        self.tagger = conversion.Tagger(config.get('styles', None))
        self.randomwords = RandomWords()
    
    def save(self):
        utils.save(self.config, self.filename)

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
