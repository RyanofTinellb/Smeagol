class Entries:
    def __init__(self, entries):
        self.entries = entries
    
    @property
    def root(self):
        return self.entries
    
    def pprint(self):
        self._pprint(self.entries)

    def _pprint(self, obj, indices: int=-1):
        if isinstance(obj, str):
            print(indices * '    ', obj)
            return
        for i, elt in enumerate(obj):
            self._pprint(elt, indices + 1)