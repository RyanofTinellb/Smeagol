class Page:
    def __init__(self, names: list, directory, entries):
        self.names = names
        self.directory = directory
        self.entries = entries
        self._data = None
    
    @property
    def location(self):
        try:
            return self._location
        except IndexError as e:
            raise f'{self.name} does not exist' from e
        except AttributeError as e:
            raise f'{self.name} is a Dictionary entry' from e
    
    @property
    def _location(self):
        location = []
        directory = self.directory
        for name in self.names:
            index = directory.index(name)
            location.append(index)
            directory = directory[index]
        return location
    
    @property
    def name(self):
        return '/'.join(self.names)

    
    @property
    def data(self):
        try:
            return self._data
        except AttributeError:
            self._data = self._find
    
    @property
    def _find(self):
        entry = self.entries
        for name in self.names:
            entry = self.entries[name]
        return entry

