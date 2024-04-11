from dataclasses import dataclass
from smeagol.utilities.types import Style


@dataclass
class Props:
    starting: bool = False
    pipe: str = ''
    separator: str = ''

    @property
    def start(self):
        sep = self.separator
        sep = f'<{sep}>' if sep and self.starting else ''
        if sep:
            self.starting = False
        return sep


    @property
    def end(self):
        sep = self.separator
        sep = f'</{sep}>' if sep and not self.starting else ''
        if sep:
            self.starting = True
        return sep
