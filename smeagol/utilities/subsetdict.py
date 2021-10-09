class SubsetDict:
    def __init__(self, values=None):
        self.values = values

    def __getattr__(self, attr):
        if not self._valid(attr):
            raise self._attribute_error
        try:
            return self.values[attr]
        except KeyError:
            return ''

    def __setattr__(self, attr, value):
            if attr == 'values':
                return super().__setattr__('values', value or {})
            if not self._valid(attr):
                raise errors.attribute_error(self)
            utils.setnonzero(self, attr, value)
    
    def _valid(self, attr):
        return attr in self._valid_attrs
    
    @property
    def _valid_attrs(self):
        pass