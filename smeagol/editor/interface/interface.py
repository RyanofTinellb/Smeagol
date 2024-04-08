from smeagol.conversion import api as conversion
from smeagol.editor.interface.system_interface import SystemInterface
from smeagol.utilities import api as utilities


class Interface(SystemInterface):

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

    def change_language(self, language):
        self.translator.select(language)
        self.randomwords.select(language)
