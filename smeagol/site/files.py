class Files:
    '''Shared file structure between Site and Interface'''

    def __init__(self, files=None):
        self.files = files or dict(
            source='', main_template='', wordlist='',
            wholepage=dict(file='', template=''),
            search=dict(index='', template='', page='',
                        template404='', page404=''),
            sections={}
        )

    def __getattr__(self, attr):
        if attr in {'source', 'main_template', 'wordlist'}:
            return self.files.setdefault(attr, '')
        elif attr in {'sections'}:
            return self.files.setdefault(attr, {})
        elif attr.startswith('wholepage_') or attr.startswith('search_'):
            attr, sub = attr.split('_')
            return self.files.setdefault(attr, {}).setdefault(sub, '')
        else:
            raise AttributeError

    def __setattr__(self, attr, value):
        if attr == 'files':
            setattr(Files, attr, value)
        elif attr in {'source', 'main_template', 'wordlist', 'sections'}:
            self.files[attr] = value
        elif attr.startswith('wholepage_') or attr.startswith('search_'):
            attr, sub = attr.split('_')
            self.files.setdefault(attr, {}).update({sub: value})
        else:
            super().__setattr__(attr, value)

    def __dir__(self):
        return self.files
