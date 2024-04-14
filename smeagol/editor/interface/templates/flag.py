from dataclasses import dataclass
from typing import Optional


@dataclass
class Flag:
    tag: Optional[str] = ''

    def __bool__(self):
        return bool(self.tag)

    def update(self, tag=''):
        self.tag = tag
