from ...utilities import utils

class Tag:
    def __init__(self, name='', rank=0, level=None, options=None):
        self.name = name
        self.rank = rank
        self.level = level or {}
        self.options = options or {}
    
    def __getattr__(self, attr):
        match attr:
            case 'hyperlink':
                return self.options.get(attr, False)
            case 'language':
                return self.options.get(attr, '%l')
            case 'block':
                return self.level.get(attr, True)
            case 'separator':
                return self.level.get(attr, '')
            case default:
                try:
                    return super().__getattr__(attr)
                except AttributeError:
                    raise errors.attribute_error(self)
    
    def __setattr__(self, attr, value):
        match attr:
            case 'hyperlink' | 'language':
                self.options[attr] = value
            case 'block' | 'separator':
                self.level[attr] = value
            case default:
                super().__setattr__(attr, value)