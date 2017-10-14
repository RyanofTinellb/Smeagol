from smeagol_site import Site
from smeagol_page import Page
from datetime import datetime

class Dictionary(Site):
    def __init__(self):
        d = Default()
        Site.__init__(self, d.destination + 'dictionary', 'Dictionary', d.source, d.template, d.markdown, d.searchjson, 2)


class Grammar(Site):
    def __init__(self):
        d = Default()
        Site.__init__(self, d.destination + 'grammar', 'Grammar', d.source, d.template, d.markdown, d.searchjson, 3)


class Story(Site):
    def __init__(self):
        d = Default()
        Site.__init__(self, d.destination + 'thecoelacanthquartet', 'The Coelacanth Quartet', d.source, d.template, d.markdown, d.searchjson, 3)


class TheCoelacanthQuartet(Story):
    def __init__(self):
        Story.__init__(self)


class Default():
    def __init__(self):
        self.destination = 'c:/users/ryan/documents/tinellbianlanguages/'
        self.source = 'data.txt'
        self.template = 'template.html'
        self.markdown = '../replacements.mkd'
        self.searchjson = 'searching.json'


if __name__ == '__main__':
    oldtime = datetime.now()
    for site in Story, Grammar, Dictionary:
        site = site()
        print(site.name + ': ')
        for x in site.publish(): print(x)
        newtime = datetime.now()
        print('100% Done: ' + str(newtime - oldtime))
        oldtime = newtime
