from ...utilities import utils

class Tag:
    def __init__(self, rank=0, tags=None, level=None, options=None):
        self.tags = tags or {}
        self.rank = rank
        self.level = level or {}
        self.options = options or {}
    
    def __getattr__(self, attr):
        match attr:
            case 'name':
                return self.tags.get(attr, '')
            case 'start':
                return self.tags.get(attr, f'<{self.name}>')
            case 'end':
                return self.tags.get(attr, f'</{self.name}>')
            case 'block':
                return self.level.get(attr, False)
            case 'separator':
                return self.level.get(attr, '')
            case 'hyperlink' | 'template':
                return self.options.get(attr, False)
            case 'language':
                return self.options.get(attr, '%l')
            case default:
                try:
                    return super().__getattr__(attr)
                except AttributeError:
                    raise errors.attribute_error(self, attr)
    
    def __setattr__(self, attr, value):
        match attr:
            case 'hyperlink' | 'language' | 'template':
                utils.setnonzero(self.options, attr, value)
            case 'block' | 'separator':
                utils.setnonzero(self.level, attr, value)
            case 'name' | 'start' | 'end':
                utils.setnonzero(self.tags, attr, value)
            case default:
                super().__setattr__(attr, value)