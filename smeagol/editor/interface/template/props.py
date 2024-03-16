class Props:
    def __init__(self):
        self.starting = False
        self.ending = False
        self.pipe = ''
        self.blocks = []

    @property
    def separator(self):
        return self.blocks[-1] if self.blocks else ''
