from ... import utils
from ...site.files import Files
from .interface import Interface
from .template import Template


class Templates(Files):
    def __init__(self, files=None):
        with utils.ignored(AttributeError):
            files = files.files
        super().__init__(files)
        self.setup_templates()
    
    def __getitem__(self, key):
        return self.sections[key]

    def set_data(self, entry, styles):
        self.entry = entry
        self.sections['contents'] = Template(str(entry), styles, self)

    def setup_templates(self):
        self.main_template = self._new(self.main_template)
        self.search_template = self._new(self.search_template)
        self.search_template404 = self._new(self.search_template404)
        self.wholepage_template = self._new(self.wholepage_template)
        for section, filename in self.sections.items():
            self.sections[section] = self._new(filename)

    def _new(self, filename):
        return Interface(filename=filename, templates=self)
