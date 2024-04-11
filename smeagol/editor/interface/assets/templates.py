from smeagol.utilities.api import SubsetDict


class Templates(SubsetDict):
    def __getattr__(self, attr):
        value = super().__getattr__(attr)
        if attr == 'sections':
            return value or {}
        return value

    def __setattr__(self, attr, value):
        # Warning: getattr and setattr are asymetrical.
        # pylint: disable=W0201, E0203
        try:
            super().__setattr__(attr, value)
        except AttributeError:
            sections = self.sections
            sections[attr] = value
            self.sections = sections

    def copy(self):
        copy = super().copy()
        copy.sections = copy.sections.copy()
        return copy

    @property
    def _valid_attrs(self):
        return (
            'main',
            'search',
            'page404',
            'wholepage',
            'sections'
        )
