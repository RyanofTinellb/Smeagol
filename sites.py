import os
import json
from datetime import datetime
from smeagol.editor.properties import Properties

class Site:
    def __init__(self, filename):
        config = f'c:/users/ryan/tinellbianlanguages/{filename}/{filename}.smg'
        self.props = Properties(config)
        self.site = self.props.site
    
    def __iter__(self):
        return self.props.site

class Grammar(Site):
    def __init__(self):
        super().__init__('grammar')

class Dictionary(Site):
    def __init__(self):
        super().__init__('dictionary')

class Story(Site):
    def __init__(self):
        super().__init__('coelacanth')

class Stories(Site):
    def __init__(self):
        super().__init__('writings')

class Stories(Site):
    def __init__(self):
        super().__init__('encyclopedia')
    
def get_list(name):
    folder = os.getenv('LOCALAPPDATA')
    inifolder = os.path.join(folder, 'Smeagol')
    inifile = os.path.join(inifolder, f'{name}.ini')
    try:
        with open(inifile) as iniload:
            return json.load(iniload)
    except (IOError, ValueError):
        return dict()

sites = get_list('site')
sites.update(get_list('dictionary'))

if __name__ == '__main__':
    oldtime = datetime.now()
    for name, filename in sites.items():
        props = Properties(filename)
        print(f'{name}:')
        print(props.site.publish())
        newtime = datetime.now()
        print(('Done: ' + str(newtime - oldtime)))
        oldtime = newtime