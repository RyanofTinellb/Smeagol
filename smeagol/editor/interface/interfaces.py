import re
from smeagol.editor.interface.interface import Interface


class Interfaces:
    def __init__(self):
        self.interfaces = {}

    def __getitem__(self, name):
        name = re.sub(r'\\+|/+', '/', name)
        try:
            return self.interfaces[name]
        except KeyError:
            interface = Interface(name)
            self.interfaces[name] = interface
            return interface

    def save_all(self):
        for interface in self.interfaces.values():
            interface.save()
            interface.save_special_files()

    def save_all_entries(self):
        for name, interface in self.interfaces.items():
            print()
            print(f'Saving from {name}:')
            interface.save_site()
            for percentage in interface.save_entries():
                if percentage >= 100:
                    continue
                print(f'{percentage}% complete')
            interface.save_special_files()
            print('100% complete')

    @property
    def blank(self):
        return Interface()

    def __iter__(self):
        return iter(self.interfaces)
