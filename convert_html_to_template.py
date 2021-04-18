import os
import re
import sys
import smeagol.filesystem as fs


class Converter:
    def __init__(self):
        root = 'C:\\Users\\Ryan.000\\TinellbianLanguages\\toplevel\\sections'
        files = fs.walk(root, lambda x: x.endswith('.html'))
        self.convert_all(files)

    def convert_all(self, files):
        for filename in files:
            text = fs.loads(filename)
            self.divs = []
            fs.save(self.convert(text), filename.replace('.html', '.json'))
            os.remove(filename)

    def convert(self, text):
        text = text.splitlines()
        text = [line.replace('{!', '<template>').replace(
            '!}', '</template>') for line in text]
        text = [self.replache(line) for line in text]
        return dict(template=text, styles={})

    def replache(self, line):
        try:
            line = re.sub(r'<(div|span) class="(.*?)">', self.resub, line)
            line = re.sub(r'</(div|span)>', lambda x: f'</{self.divs.pop()}>', line)
        except IndexError:
            line = "Error!"
        return line

    def resub(self, match):
        div = match.group(2)
        self.divs.append(div)
        return f'<{div}>'

Converter()