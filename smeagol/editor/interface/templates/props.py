from dataclasses import dataclass, field


@dataclass
class Props:
    starting: bool = False
    ending: bool = False
    pipe: str = ''
    blocks: list[str] = field(default_factory=list)

    @property
    def separator(self):
        return self.blocks[-1] if self.blocks else ''

    @property
    def start(self):
        sep = self.separator
        return f'<{sep}>' if sep else ''

    @property
    def end(self):
        sep = self.separator
        return f'</{sep}>' if sep else ''
