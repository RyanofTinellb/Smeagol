from smeagol.utilities.api import SubsetDict

class Assets(SubsetDict):
    def __init__(self, assets=None):
        super().__init__(assets)

    @property
    def _valid_attrs(self):
        return (
            'samples',
            'wordlist',
            'searchindex',
            'source'
        )
