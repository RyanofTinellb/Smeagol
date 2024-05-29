from smeagol.editor.interface.interface import Interface


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
            interface.save_special_files()

    def save_all_entries(self):
        for name, interface in self.interfaces.items():
            print()
            print(f'Saving from {name}:')
            for percentage in interface.save_entries():
                print(f'{percentage}% complete')
            interface.save_special_files()

    @property
    def blank(self):
        return Interface()

    def __iter__(self):
        return iter(self.interfaces)
