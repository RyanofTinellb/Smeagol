from smeagol.utilities import utils
from smeagol.site.page.entry import Entry


class Page(Entry):
    @property
    def analysis(self):
        wordlist = {}
        content = [str(self)]
        # remove tags, and items between some tags
        utils.change_text(
            r'\[\d\]|<(ipa|high-lulani|span).*?</\1>|<.*?>|^\d\]', ' ', content)
        # remove heading markers from tables
        utils.remove_text(r'\|\w*', content)
        # change punctuation to paragraph marks, so that splitlines works
        utils.change_text(r'[!?.|]', '\n', content)
        # change punctuation to space
        utils.change_text(r'[_()]', ' ', content)
        # remove spaces at the beginnings and end of lines,
        #    duplicate spaces and end-lines
        utils.remove_text(
            r'(?<=\n) +| +(?=[\n ])|^ +| +$|\n+(?=\n)|[,:]', content)
        # remove duplicate end-lines, and tags in square brackets
        utils.remove_text(r'\n+(?=\n)|\[.*?\]', content)
        content = content[0]
        lines = content.splitlines()
        content = [content.lower()]
        utils.change_text(r'&.*?;', ' ', content)
        # change punctuation, and tags in square brackets, into spaces
        utils.change_text(
            r'\'\"|\[.*?\]|[!?`\"/{}\\;-]|\'($| )|\d', ' ', content)
        # make glottal stops lower case where appropriate
        utils.change_text(r"(?<=[ \n])''", "'", content)
        for number, line in enumerate(content[0].splitlines()):
            for word in line.split():
                try:
                    if wordlist[word][-1] != number:
                        wordlist[word].append(number)
                except KeyError:
                    wordlist[word] = [number]
        return {'words': wordlist, 'sentences': lines}

    @property
    def link(self):
        names = [name.lower().replace(' ', '') for name in self.names[1:]]
        if not self.is_leaf:
            names += ['index']
        return names

    @property
    def url(self):
        if self.location is None:
            return 'index'
        return utils.urlform(self.name)

    def _link(self, other):
        other = self.new(other.location)
        if self == other:
            return f'<li class="normal">{self.hyperlink(other)}</li>'
        return f'<li>{self.hyperlink(other)}</li>'

    @property
    def name(self):
        return self.names[-1]
