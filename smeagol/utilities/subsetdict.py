from smeagol.utilities import utils


class SubsetDict:
    def __init__(self, values=None):
        self.values = values

    def __iter__(self):
        return ((attr, getattr(self, attr)) for attr in self._valid_attrs)

    def __str__(self):
        return str(self.values)

    def copy(self):
        return type(self)(self.values.copy())

    def update(self, updates):
        for attr in self._valid_attrs:
            self.values[attr] = getattr(updates, attr)

    def _get(self, attr):
        if not self._valid(attr):
            name = type(self).__name__
            raise AttributeError(f"'{name}' object has no attribute '{attr}'")
        try:
            return self.values[attr]
        except KeyError:
            return ''

    def __getitem__(self, attr):
        return self._get(attr)

    def __getattr__(self, attr):
        return self._get(attr)

    def __setattr__(self, attr, value):
        if attr == 'values':
            return super().__setattr__('values', value or {})
        if not self._valid(attr):
            name = type(self).__name__
            raise AttributeError(f"'{name}' object has no attribute '{attr}'")
        utils.setnonzero(self.values, attr, value)
        return None

    def _valid(self, attr):
        return attr in self._valid_attrs

    @property
    def _valid_attrs(self):
        pass
