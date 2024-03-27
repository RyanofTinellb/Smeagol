from smeagol.conversion import api as conversion
from smeagol.editor.interface.system_interface import SystemInterface
from smeagol.utilities import api as utilities
from smeagol.utilities import utils


class Interface(SystemInterface):
    def __setattr__(self, attr, value):
        match attr:
            case 'styles':
                with utils.ignored(AttributeError):
                    self.config['styles'] = dict(value.items())
        super().__setattr__(attr, value)

    def entries(self):
        return [self.find_entry(e) for e in self._entries]

    @staticmethod
    def _create_config(filename):
        return {'assets': {'source': filename}}

    def save(self):  # alias for use by (e.g.) Editor
        self.save_config()

    def setup(self, config):
        super().setup(config)
        self.language = config.get('language', '')
        self.translator = conversion.Translator(self.language)
        self.markdown = conversion.Markdown(config.get('markdown', ''))
        self.linker = conversion.Linker(config.get('links', {}))
        samples = self.assets.samples
        self.randomwords = utilities.RandomWords(self.language, samples)

    def find_entry(self, headings):
        return self.site[headings]

    def change_language(self, language):
        self.translator.select(language)
        self.randomwords.select(language)
