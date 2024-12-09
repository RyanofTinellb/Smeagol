from smeagol.utilities.api import SubsetDict


class Locations(SubsetDict):
    @property
    def _valid_attrs(self):
        return (
            'directory',
            'search',
            'page404',
            'wholepage'
        )
