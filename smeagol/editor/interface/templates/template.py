import re
from dataclasses import dataclass
from datetime import datetime as dt
from typing import Self

from smeagol.utilities import utils
from smeagol.utilities.types import Node, Styles, Tag, TemplateStore, TextTree

# pylint: disable=R0903


@dataclass
class Components:
    start: str = ''
    pipe: str = ''
    end: str = ''
    wholepage: bool = False

    def new(self, tag: Tag) -> Self:
        return type(self)(
            tag.start or self.start,
            tag.pipe,
            tag.end or self.end,
            self.wholepage
        )


def cells(text):
    segments = text.split('|')
    final = len(segments) - 1
    return ''.join([cell(s, i, final) for i, s in enumerate(segments)])


def cell(text, index, final):
    if not index or index == final or '\n' in text:
        return text
    text = text.removesuffix(' ')
    config, text = utils.try_split(text, ' ')
    spans = ''
    if (m := re.search(r'r(\d)', config)):
        spans += f' rowspan="{m.group(1)}"'
    if (m := re.search(r'c(\d)', config)):
        spans += f' colspan="{m.group(1)}"'
    d = 'h' if config and config[0] == 'h' else 'd'
    return f'<t{d}{spans}>{text}</t{d}>'


class Template:
    def __init__(self, text: TextTree, styles: Styles,
                 templates: TemplateStore, components: Components = None):
        self.text = text
        self.styles = styles
        self.templates = templates
        self.started = self.templates.started
        self.components = components or Components()

    @property
    def html(self):
        return ''.join([self._html(elt, self.components) for elt in self.text])

    def _html(self, obj, components=None, tag=None):
        components = components or Components()
        if isinstance(obj, str):
            return self.string(obj, components)
        tag = self.styles[obj.name]
        self.replace_param(obj, tag)
        components = components.new(tag)
        return self.types(tag.type)(obj, components, tag)

    def replace_param(self, obj, tag):
        if not tag.param:
            return
        text = obj.first_child
        language_code = tag.language_code if tag.language else None
        if not isinstance(text, str):
            raise ValueError(
                f'{obj.name} must have child of type <str> not of Node {text.name}')
        obj.first_child = ''.join(utils.alternate_yield([self._text, self._param],
                                                        tag.param.split('$'), text, language_code))

    @staticmethod
    def _text(text, *_args):
        return text

    def _param(self, param, text, language_code):
        url = param.startswith('url')
        if url:
            param = re.search(r'url\((.*?)\)', param).group(1)
        param, arg = utils.try_split(param, ':')
        match param:
            case 'text':
                value = text
            case 'lookup':
                value = self._lookup(arg, text, language_code)
            case _other:
                raise ValueError(f'Parameter {param} does not exist')
        return utils.url_form(value) if url else value

    def _lookup(self, arg, text, language_code):
        if not language_code:
            return self.templates.links.get(arg, {}).get(text, '')
        item = self.templates.links.get(arg, {}).get(language_code)
        try:
            return item.get(text, '')
        except AttributeError:
            return item or ''

    def types(self, type_):
        match type_:
            case 'block' | 'line' | 'div':
                function = self.block
            case 'table':
                function = self.table
            case 'data':
                function = self.data
            case 'template':
                function = self.template
            case 'heading':
                function = self.heading
            case 'link':
                function = self.link
            case _other:
                function = self.span
        return function

    def block(self, obj: Node, components: Components, tag: Tag):
        end = ''
        text = ''.join([self._html(elt, components, tag) for elt in obj])
        if self.started:
            end = self.started.tag  # + '!block!'
            self.started.update()
        return f'{tag.open}{text}{end}{tag.close}'

    def span(self, obj: Node, components: Components, tag: Tag):
        start = ''
        if not self.started:
            start = components.start  # + '!span!'
            self.started.update(components.end)
        text = ''.join([self._html(elt, components, tag) for elt in obj])
        return f'{start}{tag.open}{text}{tag.close}'

    def template(self, obj: Node, components: Components, *_args):
        name = obj.first_child
        template = self.templates[name]
        template.components = components
        try:
            return template.html
        except KeyError as e:
            raise KeyError(f'Template {name} has no tag') from e

    def heading(self, obj: Node, components: Components, tag: Tag):
        level = components.wholepage and self.templates.page.level
        tag = tag.incremented_copy(level)
        return self.block(obj, components, tag)

    def table(self, obj: Node, components: Components, tag: Tag):
        end = ''
        components = Components('<tr>|', '|', '|</tr>', components.wholepage)
        text = ''.join([self._html(elt, components, tag) for elt in obj])
        if self.started:
            end = self.started.tag  # + '!table!'
            self.started.update()
        text = cells(text.replace('//', '<br>') + end)
        return f'{tag.open}{text}{tag.close}'

    def data(self, obj: Node, components: Components, *_tag):
        match obj.first_child:
            case 'contents':
                return self.contents(components)
            case 'name':
                return self.templates.page.name
            case 'year':
                return str(dt.now().year)
            case other:
                return self._data(other)

    def _data(self, obj: str):
        function, parameter = utils.try_split(obj, '|')
        match function:
            case 'date':
                return utils.format_date(self.templates.page.date, parameter)
            case _other:
                return obj

    def contents(self, components: Components):
        text = self.templates.page.text
        styles = self.templates.styles
        template = type(self)(text, styles, self.templates, components)
        try:
            return template.html
        except KeyError as e:
            raise KeyError(f'Text {text} has no tag') from e

    def link(self, obj: Node, *_args):
        return self.templates.page.link_to(obj.first_child.split('/'))

    def string(self, text: str, components: Components):
        start = end = para = ''
        if not self.started:
            start = components.start  # + '!string!'
            self.started.update(components.end)
        text = text.replace('|', components.pipe)
        if text.endswith('\n') and self.started:
            end = self.started.tag  # + '!string!'
            self.started.update()
            text, para = text.removesuffix('\n'), '\n'
        if start and end and not text:
            return para
        return f'{start}{text}{end}{para}'
