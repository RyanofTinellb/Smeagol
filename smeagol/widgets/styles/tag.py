"""
naming:
    div | span:
        class#id
    others:
        type|class#id

properties:
    open (str): the opening tag <tag>.
    close (str): the closing tag </tag>.
    start (str): the tag placed at the start of a line <p>
    end (str): the tag placed at the end of a line </p>
    pipe (str): what to replace the pipe "|" character with within an element marked with this tag.
    language (str): a template where '%l' will be replaced with the appropriate language code.
        e.g.: ' lang="x-tlb-%l"'
    ---------
    key (str): [see below <keys: on>]
    ----
    off-key (str): [see below <keys: off>]
    ----
    keys (dict[str]):
        on (str): the keyboard shortcut used in the Sméagol editor for this tag,
                not including the `CTRL-` key.
                    e.g.: 'f' -> `CTRL-f`.
        off (str): the keyboard activity that deactivates a style, usually `Return`
            or `space`. If `space`, then the Return key will also perform this.
    ---------
    rank: controls nesting of tags, where smaller or more negative ranks are nested
            within higher ranks.

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
        anchor: -- eg: <a href="blah.html">Text</a>
            open: <a href="
            pipe: ">
            close: </a>
        span -- eg: <span class="ipa">
            open: <span class="name">
            close: </span>
        blank -- eg: some_text
            open: ''
            close: ''
            pipe: |
        label -- eg: <label for="search">
            open: <label for="wordsearch">
            close: </label>
    block-level:
                ++ Will end line tags before closing. ++
        block -- eg: <html>\n\n</html> -- typically uses starts and ends to surround lines
            open: <name>
            close: </name>
        line -- eg: <title>stuff</title> -- does not surround lines with tags
            open: <name>
            close: </name>
            start: ''
            end: ''
        heading -- eg: <h2 id="stuff">stuff</h2> -- does not surround lines with tags,
                                        increases heading level if necessary
            open: <name+d id="
            pipe: ">
            close: </name+d>
            param: $url(text)$|$node$
            start: ''
            end: ''
        ol
            open: <ol class="name">
            close: </ol>
            start: <li>
            end: </li>
        ul
            open: <ul class="name">
            close: <ul>
            start: <li>
            end: </li>
        div -- eg: <div class="flex">
            open: <div class="name">
            close: </div>
    replacement:
        error -- eg: <error><a href="http://www.tinellb.com">↑ Back to Main</a></error>
                            -- should only be displayed if an expected error occurred.
        table -- eg: <table>Entire Table</table> -- uses Markdown formatting (or similar)
        data -- eg: <entry_data>name</entry_data> -- child is passed to entry to get information
        page -- eg: <content>here</content> -- accesses main page template from Template Store
        template -- eg: <template>copyright</template> -- child is passed to Template Store
        link -- eg: <internal-link>data, stylesheets, style.css</internal-link>
                                    -- child and entry are passed to Linker to get information
        toc-<<family>> -- eg: <toc>Table of Contents / List of Links</toc> -- family
                                    is replaced by a list of groups to include
        repeat -- eg: <repeat><data>contents</data></repeat> -- used for wholepages,
                                        repeats children once for each entry
"""
import re

from smeagol.utilities import utils
from smeagol.widgets.styles.hierarchy import Hierarchy


def increment_opener(string, level):
    def inc(match, level=level):
        level += int(match.group(1))
        return f'6 class="h{level}"' if level >= 6 else str(level)
    return re.sub(r'(\d)', inc, string)


def increment_closer(string, level):
    def inc(match, level=level):
        level += int(match.group(1))
        return str(min(6, level))
    return re.sub(r'(\d)', inc, string)


def decode(type_, name):
    elt_, id_ = utils.try_split(name, '#')
    elt_, class_ = utils.try_split(elt_, '|')
    if type_ in ['div', 'span', 'ul', 'ol', 'label']:
        class_ = elt_
        elt_ = type_
    if elt_ == class_:
        class_ = ''
    return elt_, class_, id_


class Tag:
    def __init__(self, name, tags=None, **_):
        self.tags = {'type': tags} if isinstance(tags, str) else (tags or {})
        self.hierarchy = Hierarchy(self.tags.pop('hierarchy', {}))
        self.name = name
        self.elt_, self.class_, self.id_ = decode(self.type, name)
        self.language_code = ''

    def incremented_copy(self, level):
        if level > 1:
            level -= 1
        open_ = increment_opener(self.open, level)
        close = increment_closer(self.close, level)
        tags = self.tags.copy()
        tags.update({'open': open_, 'close': close})
        return type(self)(self.name, tags)

    def __getattr__(self, attr):
        try:
            return self.tags[attr]
        except KeyError:
            try:
                return self.defaults(attr)
            except AttributeError as e:
                raise AttributeError(f"{type(self).__name__} "
                                     f"'{self.name}' has no attribute '{attr}'") from e

    @property
    def key(self):
        key = self.tags.get('key') or self.tags.get('keys', {}).get('on', '')
        if isinstance(key, int):
            return f'KeyPress-{key}'
        return key

    @property
    def off_key(self):
        return self.tags.get('off-key') or self.tags.get('keys', {}).get('off', '')

    def defaults(self, attr):
        match attr:
            case 'type' | 'language' | 'repeat' | 'keep_tags' | 'sep' | 'prequel' | 'sequel':
                value = ''
            case 'param':
                value = ' id="$url(text)$|$node$' if self.type == 'heading' else ''
            case 'pipe':
                value = '">' if self.type in ('anchor', 'heading') else '|'
            case 'block':
                value = self.type in {
                    'block', 'line', 'div', 'heading', 'table', 'ol', 'ul'}
            case 'open':
                value = self.prequel + self._open
            case 'close':
                value = self._close + self.sequel
            case 'start':
                value = self._line_start
            case 'end':
                value = self._line_end
            case 'rank':
                value = self._rank
            case _default:
                try:
                    value = super().__getattr__(attr)
                except AttributeError as e:
                    raise AttributeError(
                        f"'{type(self).__name__}' object has no attribute '{attr}'") from e
        return value

    @property
    def _rank(self):
        if self.type in ('table', 'heading'):
            return 50
        if self.block:
            return 100
        if self.type == 'anchor':
            return -50
        if self.type == 'template':
            return -100
        if self.type.startswith('toc-'):
            return -50
        return 0

    @property
    def _open(self):
        lang = (f' lang="{self.language_code}"'
                if self.language and self.language_code else '')
        elt_ = self.elt_
        class_ = f' class="{self.class_}"' if self.class_ else ''
        id_ = f' id="{self.id_}"' if self.id_ else ''
        end = '>'
        match self.type:
            case 'blank':
                return ''
            case 'anchor':
                return '<a href="'
            case 'label':
                class_ = f' for="{self.class_}"'
            case 'complete':
                end = ' '
            case 'heading':
                end = ''
        return f'<{elt_}{class_}{id_}{lang}{end}'

    @property
    def _close(self):
        match self.type:
            case 'complete':
                return '>'
            case 'anchor':
                return '</a>'
            case 'blank':
                return ''
            case _other:
                return f'</{self.elt_}>'

    @property
    def _line_start(self):
        if self.sep == ' ':
            return self.sep
        if self.sep:
            return f'<{self.sep}>'
        match self.type:
            case 'line' | 'heading':
                return ''
            case 'ol' | 'ul':
                return '<li>'
            case _other:
                return None

    @property
    def _line_end(self):
        if self.sep == ' ':
            return self.sep
        if self.sep:
            return f'</{self.sep}>'
        match self.type:
            case 'line' | 'heading':
                return ''
            case 'ol' | 'ul':
                return '</li>'
            case _other:
                return None

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
            'prequel', 'sequel',
            'pipe', 'repeat', 'template', 'keep_tags'
        }
