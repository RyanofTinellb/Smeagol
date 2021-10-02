from .interface import Interface


class Interfaces:
    def __init__(self):
        self.interfaces = []
    
    @property
    def blank(self):
        try:
            return self['']
        except KeyError:
            interface = Interface('')
            self.interfaces.append(interface)
            return interface

    def __getitem__(self, filename):
        try:
            return next(filter(lambda x: x.filename == filename, self.interfaces))
        except StopIteration:
            # filename = filename.replace('\\', '/')
            raise KeyError(f'There is no Interface with filename {filename!r}')
    
    def values(self):
        for interface in interfaces:
            yield interface

    def open_site(self, filename=''):
        filename = filename or fs.open_smeagol()
        if path.isdir(filename):
            filename = self._open_folder(filename)
        try:
            self.interface = self.interfaces[filename]
        except KeyError:
            self.interface = self.interfaces[filename] = Interface(filename)
        for i, entry in enumerate(self.interface.entries):
            if i:
                self.new_tab()
            self.open_entry(entry)

    def _open_folder(self, name):
        try:
            return fs.walk(name, lambda x: fs.isfiletype(x, 'smg'))[0]
        except KeyError:
            try:
                return fs.walk(name, lambda x: fs.isfiletype(x, 'src'))[0]
            except KeyError:
                raise FileNotFoundError(
                    f'{name} does not contain a .smg or .src file')
