import json
from cwsmeagol.site.site import Site
from datetime import datetime

class Dictionary(Site):
    def __init__(self):
        d = Default()
        name = 'dictionary/'
        files = {file: d.destination + name + filename
                    for file, filename in d.files.iteritems()}
        super(Dictionary, self).__init__(d.destination + name, 'Dictionary',
            files)


class Grammar(Site):
    def __init__(self):
        d = Default()
        name = 'grammar/'
        files = {file: d.destination + name + filename
                    for file, filename in d.files.iteritems()}
        super(Grammar, self).__init__(d.destination + name, 'Grammar', files)


class Story(Site):
    def __init__(self):
        d = Default()
        name = 'coelacanth/'
        files = {file: d.destination + name + filename
                    for file, filename in d.files.iteritems()}
        super(Story, self).__init__(d.destination + name,
            'The Coelacanth Quartet', files)

class Stories(Site):
    def __init__(self):
        d = Default()
        name = 'shortstories/'
        files = {file: d.destination + name + filename
                    for file, filename in d.files.iteritems()}
        super(Stories, self).__init__(d.destination + name,
            'Short Stories', files)


class TheCoelacanthQuartet(Story):
    def __init__(self):
        super(TheCoelacanthQuartet, self).__init__()


class Default():
    def __init__(self):
        self.destination = 'c:/users/ryan/documents/tinellbianlanguages/'
        self.files = dict(source='data.json',
                          template_file='template.html',
                          searchindex='searching.json')


if __name__ == '__main__':
    oldtime = datetime.now()
    for site in Dictionary, Grammar, Story, Stories:
        site = site()
        print(site.name + ': ')
        site.update_searchindex()
        # print(site.publish())
        newtime = datetime.now()
        print('Done: ' + str(newtime - oldtime))
        oldtime = newtime
