"""
properties:
    open (str): the opening tag <tag>.
    close (str): the closing tag </tag>.
    start (str): the tag placed at the start of a line <p>
    end (str): the tag placed at the end of a line </p>
    pipe (str): what to replace the pipe "|" character with within an element marked with this tag.
    language (str): a template where '%l' will be replaced with the appropriate language code.
        e.g.: ' lang="x-tlb-%l"'
    key (str): the keyboard shortcut used in the Sméagol editor for this tag,
            not including the `CTRL-` key.
        e.g.: 'f' -> `CTRL-f`.

types:
    default:
        only contains styling information.
    inline:
                ++ Will start line tags (if appropriate) before opening. ++
        <<unspecified>> -- eg: <i>blah</i> -- this is the default tag type: "type" is left empty
            open: <name>
            close: </name>
        complete -- eg: <!doctype html>
            open: '<name '
            close: '>'
        span -- eg: <span class="ipa">
            open: <span class="name">
            close: </span>
    block-level:
                ++ Will end line tags before closing. ++
        block -- eg: <html>\n\n</html> -- typically uses starts and ends to surround lines
            open: <name>
            close: </name>
        line -- eg: <title>stuff</title> -- does not surround lines with tags
            open: <name>
            close: </name>
            start: ' '
            end: ' '
        heading -- eg: <h2>stuff</h2> -- does not surround lines with tags,
                                        increases heading level if necessary
            open: <name+d>
            close: </name+d>
            start: ' '
            end: ' '

        div -- eg: <div class="flex">
            open: <div class="name">
            close: </div>
    replacement:
        table -- eg: <table>Entire Table</table> -- uses Markdown formatting (or similar)
        data -- eg: <entry_data>name</entry_data> -- child is passed to entry to get information
        template -- eg: <template>contents</template> -- child is passed to Template Store
        link -- eg: <internal-link>data, stylesheets, style.css</internal-link>
                                    -- child and entry are passed to Linker to get information
"""

from smeagol.utilities import utils


class Tag:
    def __init__(self, name, tags=None, **_):
        self.name = name
        self.tags = tags or {}

    def __getattr__(self, attr):
        try:
            return self.tags[attr]
        except KeyError:
            try:
                return self.defaults(attr)
            except AttributeError as e:
                raise AttributeError(f"{type(self).__name__}"
                                     "'{self.name}' has no attribute '{attr}'") from e

    def defaults(self, attr):
        match attr:
            case 'type' | 'key' | 'language' | 'pipe':
                value = ''
            case 'block':
                value = self.type in {'block', 'line', 'div', 'heading'}
            case 'open':
                value = self._open
            case 'close':
                value = self._close
            case 'start' | 'end':
                value = self._line_tag
            case 'rank':
                value = 100 if self.block else 0
            case _default:
                try:
                    value = super().__getattr__(attr)
                except AttributeError as e:
                    raise AttributeError(
                        f"'{type(self).__name__}' object has no attribute '{attr}'") from e
        return value

    @property
    def _open(self):
        match self.type:
            case 'complete':
                return f'<{self.name} '
            case 'span':
                return f'<span class="{self.name}">'
            case 'div':
                return f'<div class="{self.name}">'
            case _other:
                return f'<{self.name}>'

    @property
    def _close(self):
        match self.type:
            case 'complete':
                return '>'
            case 'span':
                return '</span>'
            case 'div':
                return '</div>'
            case _other:
                return f'</{self.name}>'

    @property
    def _line_tag(self):
        return ' ' if self.type in ('line', 'heading') else ''

    def __setattr__(self, attr, value):
        if attr in self.attrs:
            utils.setnonzero(self.tags, attr, value)
            return
        super().__setattr__(attr, value)

    @property
    def attrs(self):
        return {
            'type', 'key', 'language', 'block',
            'open', 'close', 'start', 'end',
            'pipe'
        }
