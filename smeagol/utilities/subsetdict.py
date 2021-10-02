class SubsetDict:
    def __init__(self, values=None):
        self.values = values

    def __setattr__(self, attr, value):
        if attr == 'values':
            return super().__setattr__('values', value or {})
        if not self._valid(attr):
            raise self._attribute_error
        if value:
            self.values[attr] = value

    def __getattr__(self, attr):
        if not self._valid(attr):
            raise self._attribute_error
        try:
            return self.values[attr]
        except KeyError:
            return ''
    
    @property
    def _attribute_error(self):
        name = self.__class__.__name__
        return AttributeError(f"'{name}' object has no attribute '{attr}'")
    
    def _valid(self, attr):
        return attr in self._valid_attrs