from smeagol.utilities.types import TextTree, Styles, TemplateStore

# # pylint: disable=R0903


class Template:
    def __init__(self, text: TextTree, styles: Styles, templates: TemplateStore):
        self.text = text
        self.styles = styles
        self.templates = templates

    @property
    def html(self):
        return ''.join([self._html(elt) for elt in self.text])

    def _html(self, obj, sep=''):
        if isinstance(obj, str):
            return self.stringify(obj)
        style = self.styles[obj.name]
        sep = style.separator or sep
        text = ''.join([self._html(elt, style.separator) for elt in obj])
        try:
            value = self.get_text(obj, text)
        except AttributeError:
            value = text
        return value

    def get_text(self, obj, text):
        if not obj.name:
            return text
        style = self.styles[obj.name]
        if style.template:
            template = obj[0]
            return self.templates[template].html
        return f'{style.start}{text}{style.end}'

    def stringify(self, text: str):
        return text
