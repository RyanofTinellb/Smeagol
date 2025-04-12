from smeagol.editor.interface.interface import Interface
from smeagol.utilities import filesystem as fs
from smeagol.utilities import utils
FILENAME = r'c:\users\ryan\tinellbianlanguages\encyclopedia\data\encyclopedia.smg'
NEWFILE = r'c:\users\ryan\tinellbianlanguages\encyclopedia\data\assets\internal-links.glk'


class Creator:
    def __init__(self, filename, newfile):
        self.interface = Interface(filename, False)
        self.languages = {name: code for code,
                          name in self.interface.languages.items()}
        self.language = None
        self.site = self.interface.site
        self.newfile = newfile
        self.link_list = self.setup_list()
        for entry in self.site:
            self.serialise(entry)

    def setup_list(self):
        return fs.load_yaml(self.newfile,
                            default_obj={})

    def serialise(self, entry):
        link = '/'.join(entry.link)
        self.add(entry.name, link)
        self._serialise(entry.text, link)

    def _serialise(self, obj, link):
        for node in obj.nodes():
            if self.interface.styles[node.name].type == 'heading':
                url = str(node.first_child)
                self.add(url, link + '#' + url)
                continue
            self._serialise(node, link)

    def add(self, key, value):
        key, value = map(utils.url_form, [key, value])
        self.link_list.setdefault(key, value)

    def save(self):
        self.link_list = dict(self.link_list.items())
        fs.save_yaml(self.link_list, self.newfile)


Creator(FILENAME, NEWFILE).save()
