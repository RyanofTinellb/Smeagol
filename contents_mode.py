class ContentsMode:
    def __init__(self):
        self.modes = []
        self.mode = 'n'
        self.delimiter = 'p'
        self.replacements = {'t': '<table><tr><td>',
                             '/t': '</tr></table>',
                             'r': '</tr><tr><td>',
                             'n': '<ol><li>',
                             '/n': '</ol>',
                             'l': '<ul><li>',
                             '/l': '</ul>',
                             'e': '<p class="example_no_lines">',
                             'f': '<p class="example">'}
        self.delimiters =   {'n': 'p',
                             't': 'td',
                             'l': 'li'}
        self.delimiter = self.delimiters[self.mode]

    def normal(self):
        return self.mode == 'n'

    def table(self):
        return self.mode == 't'

    def list(self):
        return self.mode == 'l'

    def set(self, mode):
        if mode in ['t', 'l']:  # table, unordered list
            self.modes.append(self.mode)
            self.mode = mode
        elif mode == 'n':   # numbered list
            self.modes.append(self.mode)
            self.mode = 'l'
        elif mode.startswith('/'):   # leave mode
            try:
                self.mode = self.modes.pop()
            except IndexError:
                self.mode = 'n'
        self.delimiter = self.delimiters[self.mode]

    def delimiter(self):
        if self.mode == 'n':
            return 'p'
        elif self.mode == 't':
            return 'td'
        elif self.mode == 'l':
            return 'li'
