from smeagol.editor.interface.system_interface import SystemInterface
from smeagol.utilities import api as utilities


class Interface(SystemInterface):
    def __init__(self, *args, **kwargs):
        self.languages = None
        self.randomwords = None
        self.imes = None
        super().__init__(*args, **kwargs)

    def __getattr__(self, attr):
        match attr:
            case '_imes':
                return self.config.get('imes', {})
            case _default:
                try:
                    return super().__getattr__(attr)
                except AttributeError as e:
                    name = type(self).__name__
                    raise AttributeError(
                        f"'{name}' object has no attribute '{attr}'") from e

    @staticmethod
    def _create_config(filename):
        return {'assets': {'source': filename}}

    def save(self):  # alias for use by (e.g.) Editor
        self.save_config()

    def setup(self, config):
        super().setup(config)
        self.languages = self.load_from_config('languages', {})

    def change_language(self, language):
        self.randomwords.select(language)
