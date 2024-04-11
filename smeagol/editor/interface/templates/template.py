from smeagol.utilities.types import TextTree, Styles, TemplateStore

# # pylint: disable=R0903


class Template:
    def __init__(self, text: TextTree, styles: Styles, templates: TemplateStore):
        self.text = text
        self.styles = styles
        self.templates = templates
        self.props = self.templates.props

    @property
    def html(self):
        return ''.join([self._html(elt) for elt in self.text])

    def _html(self, obj):
        if isinstance(obj, str):
            return self.string(obj)
        self.props.style = style = self.styles[obj.name]
        self.props.pipe = self.props.pipe or style.pipe
        if style.block:
            return self.block(obj)
        if style.template:
            return self.template(obj)
        # if style.table:
        #     return self.table(obj)
        return self.span(obj)

    def block(self, obj):
        style = self.props.style
        self.props.separator = style.separator or self.props.separator
        text = ''.join([self._html(elt) for elt in obj])
        end = self.props.end # .replace('>', '>!block!')
        return f'{style.start}{text}{end}{style.end}'

    def span(self, obj):
        start = self.props.start # .replace('>', '>!span!')
        style = self.props.style
        text = ''.join([self._html(elt) for elt in obj])
        end = self.props.end # .replace('>', '>!span!')
        return f'{start}{style.start}{text}{style.end}{end}'

    def template(self, obj):
        template = obj[0]
        return self.templates[template].html

    def string(self, text: str):
        start = self.props.start # .replace('>', '>!string!')
        text = text.replace('|', self.props.pipe)
        if text.endswith('\n') and not self.props.starting:
            end = self.props.end # .replace('>', '>!string!')
            text = text.removesuffix('\n') + end + '\n'
        return f'{start}{text}'
