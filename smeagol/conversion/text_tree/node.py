class Node:
    def __init__(self, parent=None, name: str = None) -> None:
        self.parent = parent
        self.name = name or ''
        self.children = []

    @property
    def open_tag(self):
        return f'<{self.name}>' if self.name else ''
    
    @property
    def close_tag(self):
        return f'</{self.name}>' if self.name else ''
    
    @property
    def middle_text(self):
        return ''.join((str(child) for child in self.children))

    def __iter__(self):
        return iter(self.children)

    def __iadd__(self, other):
        self.children.append(other)
        return self

    def __str__(self):
        return f'{self.open_tag}{self.middle_text}{self.close_tag}'
    
    