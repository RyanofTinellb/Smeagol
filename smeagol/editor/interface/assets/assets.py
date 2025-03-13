from smeagol.utilities.api import SubsetDict


class Assets(SubsetDict):
    @property
    def _valid_attrs(self):
        return (
            'wordlist',
            'searchindex',
            'source'
        )
