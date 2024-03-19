class Directory:
    def __init__(self, directory: dict[dict | list]):
        self.directory = directory or {}
    
    def index(self, value):
        try:
            return self.directory.index(value)
        except AttributeError:
            for i, name in self.directory:
                if name == value:
                    return i
