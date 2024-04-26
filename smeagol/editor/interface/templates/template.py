import re
from dataclasses import dataclass
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
        components = components.new(tag)
        return self.types(tag.type)(obj, components, tag)

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
        name = obj[0]
        template = self.templates[name]
        template.components = components
        return template.html

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
        match obj[0]:
            case 'contents':
                return self.contents(components)
            case 'name':
                return self.templates.page.name
            case _other:
                return str(obj[0])

    def contents(self, components: Components):
        text = self.templates.page.text
        styles = self.templates.styles
        template = type(self)(text, styles, self.templates, components)
        return template.html

    def link(self, obj: Node, *_args):
        return self.templates.page.link_to(obj[0].split('/'))

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
