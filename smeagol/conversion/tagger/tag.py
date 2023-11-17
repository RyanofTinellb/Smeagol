from ...utilities import errors, utils

'''
properties:
    name (str)
    start (str): the opening tag <tag>.
    end (str): the closing tag </tag>.
    block (bool): whether the element is block-level (True) or inline (False).
    pipe (str): what to replace the pipe "|" character with within an element marked with this tag.
    separator (str): the tag name to be placed at the beginning and end of each line.
        e.g.: 'p' in '<p>This is a line</p>'.
    language (str): a template where '%l' will be replaced with the appropriate language code.
        e.g.: ' lang="x-tlb-%l"'
    hyperlink (bool): whether text with this tag should be replaced with a hyperlink.
    template (bool): whether text with this tag refers to a template.
    key (str): the keyboard shortcut used in the Sméagol editor for this tag,
            not including the `CTRL-` key.
        e.g.: 'f' -> `CTRL-f`.
'''


class Tag:
    def __init__(self, rank=0, tags=None, **_):
        self.rank = rank
        self.options = tags or {}

    def __getattr__(self, attr):
        try:
            return self.options[attr]
        except KeyError:
            return self.default(attr)

    def default(self, attr):
        match attr:
            case 'start':
                return f'<{self.name}>'
            case 'end':
                return f'</{self.name}>'
            case 'block' | 'hyperlink' | 'template':
                return False
            case 'pipe' | 'separator' | 'key':
                return ''
            case 'language':
                return '%l'
            case default:
                try:
                    return super().__getattr__(attr)
                except AttributeError:
                    raise errors.throw_error(AttributeError, self, attr)

    def __setattr__(self, attr, value):
        if attr in self.attrs:
            utils.setnonzero(self.options, attr, value)
            return
        super().__setattr__(attr, value)

    @property
    def attrs(self):
        return {
            'hyperlink', 'language', 'template', 'block', 'separator',
            'name', 'start', 'end', 'pipe'
        }