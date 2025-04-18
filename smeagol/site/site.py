from smeagol.site.page.page import Page
from smeagol.utilities import utils


class Site(Page):
    def __init__(self, *args, **kwargs):
        self.serialisation_format = kwargs.pop('serialisation_format', {})
        self.serialiser = self._serialiser(self.serialisation_format)
        super().__init__(*args, **kwargs)
        self.current = self.root
        self._analysis.update({
            'urls': [],
            'pages': []
        })
        self._wordlist = []
        self._serial = {'t': '', 'l': '', 'p': '', 'd': '', 'n': ''}

    def __getattr__(self, attr):
        match attr:
            case 'urls' | 'pages':
                return self._analysis[attr]
        try:
            return super().__getattr__(attr)
        except AttributeError as e:
            name = type(self).__name__
            raise AttributeError(
                f"'{name}' object has no attribute '{attr}'") from e

    def __len__(self):
        return sum(1 for page in self)

    @property
    def hierarchy(self):
        for names in self.directory:
            yield self.new(names)

    def add_entry(self, page: Page):
        self.entries.add(page.names)
        with utils.ignored(IndexError):
            self.directory.add(page.names)

    def remove_entry(self, page: Page):
        self.entries.remove(page.names.copy())
        with utils.ignored(IndexError):
            self.directory.remove(page.names.copy())

    def new(self, values: list[str] | list[int] = None) -> Page:
        values = values or [self.entries.name]
        with utils.ignored(TypeError):
            values = self.directory[values].names
        return Page(self.directory, self.entries, values[:])

    @property
    def root(self):
        return self.new()

    # @property
    def analysis(self):
        for obj in self._analysis.values():
            obj.clear()
        self.lines.clear()
        for entry_number, entry in enumerate(self):
            base = len(self.lines)
            analysis = entry.analysis()
            self.urls.append(entry.url)
            self.pages.append(entry.name)
            self.lines.extend(entry.lines)
            self._add_terms(analysis, base, entry_number)
        return self._analysis

    def _add_terms(self, analysis, base, entry_number):
        for term, line_numbers in analysis['terms'].items():
            line_numbers = utils.increment(line_numbers, by=base)
            locations = {str(entry_number): sorted(line_numbers)}
            self.terms.setdefault(term, {}).update(locations)

    # @property
    def serialisation(self):
        if not self.serialisation_format:
            return []
        self._wordlist.clear()
        for entry in self:
            self._serial['t'] = utils.buy_caps(entry.name)
            self._serialise(entry.text)
        return self._wordlist

    def _serialise(self, node):
        for child in node.nodes():
            self.serialiser.get(child.name, self._serialise)(child)

    def _language(self, node):
        self._serial['l'] = node.stringify()
        self._serial['n'] = ''

    def _pos(self, node):
        self._serial['p'] = node.stringify()

    def _native_script(self, node):
        self._serial['n'] = node.stringify()

    def _pronunciation(self, node):
        self._serial['r'] = node.stringify().strip('/')

    def _definition(self, node):
        self._serial['d'] = utils.buy_caps(node.stringify())
        self._wordlist.append(self._serial.copy())

    def _serialiser(self, serial):
        if not serial:
            return []
        return {
            serial['language']: self._language,
            serial['part of speech']: self._pos,
            serial['definition']: self._definition,
            serial['native script']: self._native_script,
            serial['pronunciation']: self._pronunciation
        }
