from Edit import *

class EditStory(Edit):
    def __init__(self, directory, datafile, site, markdown, master=None):
        self.font = ('Californian FB', 16)
        self.widgets = [3, 3, 'languages']
        Edit.__init__(self, directories=directory, datafiles=datafile, sites=site, markdowns=markdown)
