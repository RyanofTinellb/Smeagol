class Files:
    '''Shared file structure between Site and Interface'''

    def __init__(self, files=None):
        self.files = files or dict(
            source='', template_file='', wordlist='',
            wholepage=dict(file='', template=''),
            search=dict(index='', template='', page='',
                        template404='', page404=''),
            sections={}
        )

    def __getattr__(self, attr):
        if attr in {'source', 'template_file', 'wordlist'}:
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
        elif attr in {'source', 'template_file', 'wordlist', 'sections'}:
            self.files[attr] = value
        elif attr.startswith('wholepage_') or attr.startswith('search_'):
            attr, sub = attr.split('_')
            self.files.setdefault(attr, {}).update({sub: value})
        else:
            raise AttributeError

    @property
    def templates(self):
        return {
            'main': dict(filename=self.template_file),
            'wholepage': dict(filename=self.wholepage_template),
            'search': dict(filename=self.search_template),
            '404': dict(filename=self.search_template404)}

    def __dir__(self):
        return self.files
