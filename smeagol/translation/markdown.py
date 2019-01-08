import os
from smeagol.defaults import default

class Markdown:
    def __init__(self, filename=None):
        self.markup, self.markdown = [], []
        self.source = None
        self.destination = None
        self.filename = filename
        self.setup(filename)

    def setup(self, filename):
        if filename:
            with open(filename) as replacements:
                for line in replacements:
                    self.append_markdown(line)
        else:
            for line in default.markdown.splitlines():
                self.append_markdown(line)

    def __str__(self):
        try:
            with open(self.filename) as markdown:
                return markdown.read()
        except IOError:
            return ''

    def append_markdown(self, line):
        line = line.replace(r'\n', '\n')
        line = line.split(' | ')
        try:
            self.markdown.append(line[1])
            self.markup.append(line[0])
        except IndexError:
            pass

    def to_markup(self, text):
        self.source, self.destination = self.markdown[::-1], self.markup[::-1]
        return self.convert(text)

    def to_markdown(self, text):
        self.source, self.destination = self.markup, self.markdown
        return self.convert(text)

    def convert(self, text):
        for first, second in zip(self.source, self.destination):
            text = text.replace(first, second)
        return text

    def find_formatting(self, keyword):
        """
        Find markdown for specific formatting.
        :param keyword (str): the formatting type, in html, e.g.: strong, em, &c, &c.
        :return (tuple): the opening and closing tags, in markdown, e.g.: ([[, ]]), (<<, >>)
        """
        start = self.find('<' + keyword + '>')
        if start == '':
            start = self.find('<' + keyword)
        end = self.find('</' + keyword + '>')
        return start, end

    def find(self, text):
        """
        Find markdown for particular formatting.
        :param text (str):
        """
        try:
            return self.to_markdown(text)
        except ValueError:
            return ''

    def refresh(self, new_markdown=''):
        if new_markdown and self.filename:
            with open(self.filename, 'w') as markdown:
                markdown.write(new_markdown)
        self.markup, self.markdown = [], []
        self.source = None
        self.destination = None
        self.setup(self.filename)
