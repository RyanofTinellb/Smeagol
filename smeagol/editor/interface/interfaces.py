import os.path

from ...utilities import filesystem as fs
from ...utilities import utils
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
            self.interfaces.append(interface := Interface(filename))
            return interface
    
    def __iter__(self):
        return iter(self.interfaces)
    
    def save_all(self):
        for interface in self.interfaces:
            self._save(interface)
    
    def _save(self, interface):
        with utils.ignored(IOError):
            interface.save()

    def open_site(self, filename=''):
        filename = filename or fs.open_smeagol()
        if fs.isfolder(filename):
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
            return fs.findbytype(name, '.smg')[0]
        except KeyError:
            try:
                return fs.findbytype(name, '.src')[0]
            except KeyError:
                raise FileNotFoundError(
                    f'{name} does not contain a .smg or .src file')
