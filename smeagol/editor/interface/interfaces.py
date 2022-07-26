import os.path

from ...utilities import filesystem as fs
from ...utilities import utils
from .interface import Interface


class Interfaces:
    def __init__(self):
        self.interfaces = {}
    
    def __getitem__(self, name):
        try:
            return self.interfaces[name]
        except KeyError:
            interface = Interface(name)
            self.interfaces[name] = interface
            return interface
        
    def save_all(self):
        for interface in self.interfaces.values():
            interface.save()
    
    @property
    def blank(self):
        return Interface()
    
    def __iter__(self):
        return iter(self.interfaces)