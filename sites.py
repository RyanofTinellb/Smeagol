import json
from smeagol.site.site import Site
from datetime import datetime

class Dictionary(Site):
    def __init__(self):
        d = Default()
        name = 'dictionary/'
        files = {file: d.destination + name + filename
                    for file, filename in d.files.items()}
        super(Dictionary, self).__init__(d.destination + name, 'Dictionary',
            files)


class Grammar(Site):
    def __init__(self):
        d = Default()
        name = 'grammar/'
        files = {file: d.destination + name + filename
                    for file, filename in d.files.items()}
        super(Grammar, self).__init__(d.destination + name, 'Grammar', files)


class Story(Site):
    def __init__(self):
        d = Default()
        name = 'coelacanth/'
        files = {file: d.destination + name + filename
                    for file, filename in d.files.items()}
        super(Story, self).__init__(d.destination + name,
            'The Coelacanth Quartet', files)

class Stories(Site):
    def __init__(self):
        d = Default()
        name = 'writings/'
        files = {file: d.destination + name + filename
                    for file, filename in d.files.items()}
        super(Stories, self).__init__(d.destination + name,
            'Short Stories', files)

class Encyclopedia(Site):
    def __init__(self):
        d = Default()
        name = 'encyclopedia/'
        files = {file: d.destination + name + filename
                    for file, filename in d.files.items()}
        super(Stories, self).__init__(d.destination + name,
            'The Universe of Tinellb', files)


class TheCoelacanthQuartet(Story):
    def __init__(self):
        super(TheCoelacanthQuartet, self).__init__()


class Default():
    def __init__(self):
        self.destination = 'c:/users/ryan/tinellbianlanguages/'
        self.files = dict(source='data.src',
                          template_file='template.html',
                          searchindex='searching.json')
        self.files = dict(source='data.src',
                          template_file='template.html',
                          wholepage=dict(file='wholepage.html',
                                         template='wholetemplate.html'),
                          search=dict(index='searching.json',
                                      template='',
                                      page='',
                                      template404='',
                                      page404='')
        )


if __name__ == '__main__':
    oldtime = datetime.now()
    for site in Story, Stories, Dictionary, Grammar:
        site = site()
        print((site.name + ': '))
        print((site.publish()))
        newtime = datetime.now()
        print(('Done: ' + str(newtime - oldtime)))
        oldtime = newtime
