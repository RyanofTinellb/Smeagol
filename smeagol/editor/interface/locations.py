from ...utilities.api import SubsetDict


class Locations(SubsetDict):
    def __init__(self, locations=None):
        super().__init__(locations)

    @property
    def _valid_attrs(self):
        return (
            'directory',
            'search',
            'page404',
            'wholepage'
        )
