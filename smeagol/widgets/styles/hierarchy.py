from smeagol.utilities.subsetdict import SubsetDict
from smeagol.utilities import utils

class Hierarchy(SubsetDict):
    def __bool__(self):
        return bool(self.values)

    @property
    def start(self):
        tag, class_ = utils.try_split(self.tag, '|', '')
        class_ = class_ and f' class="{class_}"'
        return tag and f'<{tag}{class_}>'

    @property
    def end(self):
        tag, _class = utils.try_split(self.tag, '|', '')
        return tag and f'</{tag}>'

    @property
    def _valid_attrs(self):
        return ('rank', 'key', 'save', 'tag', 'function')
