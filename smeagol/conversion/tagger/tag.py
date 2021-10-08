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
                return utils.default_getter(self, attr)
    
    def __setattr__(self, attr, value):
        match attr:
            case 'hyperlink' | 'language':
                self.options[attr] = value
            case 'block' | 'separator':
                self.level[attr] = value
            case default:
                utils.default_setter(self, attr, value)