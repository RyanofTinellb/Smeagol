import json
from cwsmeagol.site.smeagol_site import Site
from cwsmeagol.site.smeagol_page import Page
from cwsmeagol.editor.smeagol_files import Files
from datetime import datetime
from collections import namedtuple

class Dictionary(Site):
    def __init__(self):
        d = Default()
        name = 'dictionary/'
        files = Files(*map(lambda file_: d.destination + name + file_, d.files))
        super(Dictionary, self).__init__(d.destination + name, 'Dictionary',
            files, 2)


class Grammar(Site):
    def __init__(self):
        d = Default()
        name = 'grammar/'
        files = Files(*map(lambda file_: d.destination + name + file_, d.files))
        super(Grammar, self).__init__(d.destination + name, 'Grammar', files, 3)


class Story(Site):
    def __init__(self):
        d = Default()
        name = 'thecoelacanthquartet/'
        files = Files(*map(lambda file_: d.destination + name + file_, d.files))
        super(Story, self).__init__(d.destination + name,
            'The Coelacanth Quartet', files, 3)


class TheCoelacanthQuartet(Story):
    def __init__(self):
        super(TheCoelacanthQuartet, self).__init__()


class Default():
    def __init__(self):
        self.destination = 'c:/users/ryan/documents/tinellbianlanguages/'
        files = namedtuple('files', ['source', 'template', 'markdown', 'searchjson'])
        self.files = files(source='data.txt',
                           template='template.html',
                           markdown='../replacements.mkd',
                           searchjson='searching.json')


if __name__ == '__main__':
    oldtime = datetime.now()
    for site in Story, Grammar, Dictionary:
        site = site()
        print(site.name + ': ')
        site.publish()
        newtime = datetime.now()
        print('100% Done: ' + str(newtime - oldtime))
        oldtime = newtime
