from ..utils import *
from ..errors import SectionFileNotFoundError

import re


class Templates:
    def __init__(self, templates=None, sections=None):
        templates = templates or []
        self.files = sections or {} # {name: filename}
        self.sections = {}  # {name: text} //subsidiary templates
        self.templates = {} # {name: text} //main templates to return
        for filename, name, error in templates:
            text = self.open(filename, error)
            self.templates[name] = self.sub(text)

    def sub(self, regex):
        with ignored(AttributeError):
            regex = self.get(regex.group(1))
        return re.sub(r'{!(.*?)!}', self.sub, regex)
    
    def get(self, name):
        try:
            text = self.sections[name]
        except KeyError:
            try:
                text = self.open(self.files[name])
            except FileNotFoundError:
                raise SectionFileNotFoundError(name)
            self.sections[name] = text
        return text
    
    def open(self, filename, error=FileNotFoundError):
        if filename:
            try:
                with open(filename, encoding='utf-8') as template:
                    return template.read()
            except FileNotFoundError:
                raise error
        else:
            return ''

    def items(self):
        for name, text in self.templates.items():
            yield name, text