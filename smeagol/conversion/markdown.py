import os
import json
from smeagol.defaults import default
from smeagol.errors import MarkdownFileNotFoundError
from smeagol import utils


class Markdown:
    def __init__(self, markdown=None):
        '''@param markdown: filename (str) || markdown (dict[])'''
        try:
            self.replacements = self.load(markdown)
            self.filename = markdown
        except TypeError:
            self.replacements = markdown

    def load(self, filename):
        try:
            return utils.load(filename)
        except FileNotFoundError:
            raise MarkdownFileNotFoundError
    
    def save(self, filename):
        utils.dump(self.replacements, filename)

    def to_markup(self, text):
        for replacement in reversed(self.replacements):
            text = text.replace(replacement['markdown'], replacement['markup'])
        return text

    def to_markdown(self, text):
        for replacement in self.replacements:
            text = text.replace(replacement['markup'], replacement['markdown'])
            if not replacement['display_markdown']:
                text = text.replace(replacement['markdown'], replacement['markup'])
        return text