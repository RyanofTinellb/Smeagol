from smeagol.utilities import filesystem as fs

class SerialNumberer:
    def __init__(self):
        filename = 'c:/users/ryan/tinellbianlanguages/dictionary/data/assets/alphabet.srt'
        self.alphabet = fs.load_yaml(filename)

    def change(self, name):
        if name.startswith('ʔ'):
            name = '$’' + name.removeprefix('ʔ')
        name = name.replace('ʔ', '’’')
        code = '1' if name.startswith('-') else '2' if name.startswith('$') else '0'
        name = name.removeprefix('-').removeprefix('$')
        code += '1' if name.endswith('-') else '0'
        name = name.removesuffix('-')
        index = 0
        serial = ''
        while index < len(name):
            change = False
            for length, replacement in self.alphabet['replacements'].items():
                r = replacement.get(name[index:index+length], None)
                if r:
                    code += str(r[0])
                    serial += self.alphabet['sort order'][r[1]]
                    index += length
                    change = True
                    break
            if not change:
                code += str(0)
                serial += self.alphabet['sort order'][name[index]]
                index += 1
        return serial, code