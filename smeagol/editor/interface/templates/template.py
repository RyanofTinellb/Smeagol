import re
from dataclasses import dataclass
from datetime import datetime as dt
from typing import Self, Optional

from smeagol.utilities import utils
from smeagol.utilities.types import Styles, Tag, TemplateStore, TextTree
from smeagol.conversion.text_tree.node import Node

# pylint: disable=R0903


@dataclass
class Components:
    start: Optional[str] = None
    pipe: Optional[str] = ''
    end: Optional[str] = None
    wholepage: bool = False

    def new(self, tag: Tag) -> Self:
        return type(self)(
            tag.start if tag.start is not None else self.start,
            tag.pipe,
            tag.end if tag.end is not None else self.end,
            self.wholepage
        )


def _text(text, *_args):
    return text


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
    def __init__(self, text: TextTree, title: TextTree, styles: Styles,
                 templates: TemplateStore, components: Components = None):
        self.text = text
        self.title = title
        self.styles = styles or templates.styles
        self.templates = templates
        self.started = self.templates.started
        self.hierarchy = []
        self._level = -1
        self.components = components or Components()

    @property
    def html(self):
        html = ''.join([self._html(elt, self.components) for elt in self.text])
        html += ''.join(reversed(self.hierarchy))
        return re.sub(fr'<a href="{self.templates.page.name}\.html.*?">(.*?)</a>',
                      r'<span class="self-link">\1</span>', html)

    def _html(self, obj, components=None):
        components = components or Components()
        if isinstance(obj, str):
            return self.string(obj, components)
        try:
            tag = self.styles[obj.name]
        except KeyError as e:
            raise KeyError(f'Tag {obj.name} does not exist') from e
        return self.section(obj, components, tag)

    def section(self, obj, components, tag):
        composition = self.compose(obj, components, tag)
        new_rank = tag.hierarchy.rank
        if not new_rank:
            return composition
        difference = new_rank - len(self.hierarchy)
        self.hierarchy += [''] * difference
        prequel = ''
        while len(self.hierarchy) > new_rank:
            prequel += self.hierarchy.pop()
        prequel += tag.hierarchy.start
        self.hierarchy.append(tag.hierarchy.end)
        return ''.join([prequel, composition])

    def compose(self, obj, components, tag):
        components = components.new(tag)
        if tag.param and tag.type != 'toc':
            return self.replace_param(obj, components, tag)
        return self.types(tag)(obj, components, tag)

    def replace_param(self, obj, components, tag):
        _, language_code = (utils.try_split(
            obj.name, '@')) if tag.language else (None, None)
        node = Node()
        options = [obj, components, language_code]
        try:
            node.add(''.join(utils.alternate_yield([_text, self._param],
                                                   tag.param.split('$'), *options)))
        except (IndexError, ValueError):  # usually a broken link
            return self._html(obj.other_child, components)
        except TypeError as e:
            raise TypeError(obj, tag.param) from e
        return self.types(tag)(node, components, tag)

    def _param(self, param, obj, components, language_code):
        text = obj.stringify(skip='error')
        url, param = self._extract('url', param)
        upper, param = self._extract('upper', param)
        param, arg = utils.try_split(param, ':')
        match param:
            case 'node':
                value = ''.join([self._html(elt, components) for elt in obj])
            case 'text':
                value = text
            case 'lookup':
                value = self._lookup(arg, text, language_code)
            case 'link':
                value = self._link(arg, text, language_code)
            case _other:
                raise ValueError(f'Parameter {param} does not exist')
        return utils.url_form(value) if url else utils.buy_caps(value) if upper else value

    def _extract(self, tag, param):
        if param.startswith(tag):
            return True, re.search(fr'{tag}\((.*?)\)', param).group(1)
        return False, param

    def _link(self, arg, text, language_code):
        arg, data = utils.try_split(arg, ':')
        match arg:
            case 'next':
                page = self.templates.page.next_page()
            case 'previous':
                page = self.templates.page.previous_page()
            case 'lookup':
                page = self._lookup(data, text, language_code)
            case other:
                raise NotImplementedError(
                    f'function {other} has not been implemented')
        return utils.link(page)

    def _lookup(self, arg, text, language_code):
        text = text.lower().replace(' ', '')
        if not language_code:
            item = self.templates.links.get(arg, {}).get(text, '')
        else:
            item = self.templates.links.get(arg, {}).get(language_code, {})
            with utils.ignored(AttributeError):
                item = item.get(text, '')
        if not item:
            print('This didn’t work!', arg, text, language_code)
        return item

    #pylint: disable=R0911
    def data(self, obj: Node, components: Components, *_tag):
        match obj.first_child:
            case 'contents':
                return self.contents(components)
            case 'name':
                return utils.buy_caps(self.templates.page.name)
            case 'year':
                return str(dt.now().year)
            case 'entry-title':
                return self.templates.entry_title
            case 'title':
                return ''.join([self._html(elt, self.components) for elt in self.templates.title])
            case 'root':
                return self.templates.page.root.name
            case other:
                return self._data(other)

    def _data(self, obj: str):
        function, parameter = utils.try_split(obj, '|')
        match function:
            case 'date':
                return utils.format_date(self.templates.page.date, parameter)
            case _other:
                return obj

    def types(self, tag):
        try:
            function = getattr(self, tag.type)
        except AttributeError:
            function = self.block if tag.block else self.span
        return function

    def repeat(self, obj, components, _tag):
        try:
            return ''.join([self._repeat(entry, obj, components)
                            for entry in self.templates.page.hierarchy])
        except KeyError:
            return ''.join([self._repeat(entry, obj, components) for entry in self.templates.page])

    def _repeat(self, entry, obj, components):
        if entry.level == 1:
            return ''
        self.templates.page = entry
        return ''.join([self._html(elt, components) for elt in obj])

    def toc(self, obj, _components, tag):
        self._level = -1
        open_tags = []
        output = ''
        page = self.templates.page
        try:
            family = page.reunion(obj.first_child.split('-'))
        except ValueError:
            family = page.root.reunion(obj.first_child.split('-'))
        except IndexError: # page is a dictionary entry
            return ''
        for entry in self.templates.page.hierarchy:
            if entry in family:
                for _ in range(max(0, self._level - entry.level)):
                    with utils.ignored(IndexError):
                        output += open_tags.pop()
                num = max(0, entry.level -
                          self._level) if self._level > -1 else 1
                for _ in range(num):
                    if open_tags:
                        output += tag.start + tag.open
                        open_tags += [tag.close + tag.end]
                    else:
                        output += tag.open
                        open_tags = [tag.close]
                self._level = entry.level
                output += tag.start or ''
                if entry == page:
                    output += entry.name
                else:
                    output += tag.param.replace('$link$', utils.link(entry)
                                                ).replace('$name$', entry.name)
                output += tag.end or ''
        output += ''.join(reversed(open_tags))
        return output

    def error(self, obj, components, _tag):
        return ''.join([self._html(elt, components) for elt in obj])

    def block(self, obj: Node, components: Components, tag: Tag):
        end = ''
        text = ''.join([self._html(elt, components) for elt in obj])
        if self.started:
            end = self.started.tag  # + '!block!'
            self.started.update()
        return f'{tag.open}{text}{end}{tag.close}'

    def span(self, obj: Node, components: Components, tag: Tag):
        start = ''
        if not self.started:
            start = components.start or ''  # + '!span!'
            self.started.update(components.end or '')
        text = ''.join([self._html(elt, components) for elt in obj])
        return f'{start}{tag.open}{text}{tag.close}'

    def template(self, obj: Node, components: Components, *_args):
        name = obj.first_child.lower().replace(' ', '')
        try:
            template = self.templates[name]
        except KeyError:
            return ''
        template.components = components
        try:
            return template.html
        except KeyError as e:
            raise KeyError(f'Template {name} is missing a tag') from e

    def heading(self, obj: Node, components: Components, tag: Tag):
        level = components.wholepage and self.templates.page.level
        tag = tag.incremented_copy(level)
        return self.block(obj, components, tag)

    def table(self, obj: Node, components: Components, tag: Tag):
        end = ''
        components = Components('<tr>|', '|', '|</tr>', components.wholepage)
        text = ''.join([self._html(elt, components) for elt in obj])
        if self.started:
            end = self.started.tag  # + '!table!'
            self.started.update()
        text = cells(text + end)
        return f'{tag.open}{text}{tag.close}'

    def contents(self, components: Components):
        text = self.templates.page.text
        title = self.templates.page.title
        styles = self.templates.styles
        template = type(self)(text, title, styles, self.templates, components)
        try:
            return template.html
        except KeyError as e:
            raise KeyError(f'Unable to generate html from entry <{
                           self.templates.page.name}>') from e

    def link(self, obj: Node, *_args):
        return utils.link(obj.first_child.split('/'))

    def string(self, text: str, components: Components):
        start = end = para = ''
        if not self.started:
            start = components.start or ''  # + '!string!'
            self.started.update(components.end)
        text = text.replace('|', components.pipe)
        if text.endswith('\n') and self.started:
            end = self.started.tag  # + '!string!'
            self.started.update()
            text, para = text.removesuffix('\n'), '\n'
        if start and end and not text:
            return para
        return f'{start}{text}{end}{para}'
