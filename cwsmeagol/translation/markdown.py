import os

class Markdown:
    def __init__(self, filename=None):
        """
        Marking down proceeds down the Replacements page
        :param filename (String): the path to the replacements file
        :raise IOError: filename does not exist
        """
        if filename is None:
            filename = os.path.join(os.path.dirname(__file__), 'markdown.mkd')
        self.markup, self.markdown = [], []
        self.source = None
        self.destination = None
        self.filename = filename
        if filename:
            with open(filename) as replacements:
                for line in replacements:
                    line = line.split(" ")
                    self.markup.append(line[0])
                    self.markdown.append(line[1])

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

    def refresh(self):
        self.markup, self.markdown = [], []
        self.source = None
        self.destination = None
        if self.filename:
            with open(self.filename) as replacements:
                for line in replacements:
                    line = line.split(" ")
                    self.markup.append(line[0])
                    self.markdown.append(line[1])
