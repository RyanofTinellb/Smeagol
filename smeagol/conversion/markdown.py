import os
import json
from smeagol.defaults import default
from smeagol.errors import MarkdownFileNotFoundError
from smeagol import utils


class Markdown:
    def __init__(self, arg=None):
        '''@param markdown: filename (str) || markdown (dict[])'''
        arg = arg or []
        try:
            self.load(arg)
        except (TypeError, AttributeError):
            self.replacements = arg
            self.filename = ''
        
    def __getitem__(self, index):
        return self.replacements[index]
    
    def __iadd__(self, item):
        self.replacements.append(item)
        return self
    
    @property
    def non_blank(self):
        return [r for r in self if r['markdown']]
    
    def copy(self):
        if self.filename:
            return __class__(self.filename)
        else:
            return __class__(self.replacements)

    def load(self, filename=''):
        self.filename = filename or self.filename
        try:
            self.replacements = utils.load(self.filename)
        except FileNotFoundError:
            raise MarkdownFileNotFoundError
    
    def save(self, filename=''):
        self.filename = filename or self.filename
        try:
            utils.save(self.non_blank, self.filename)
        except FileNotFoundError:
            raise MarkdownFileNotFoundError

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