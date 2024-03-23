from smeagol.editor.interface.templates.props import Props
from smeagol.utilities.types import TextTree, Styles, TemplateStore

# pylint: disable=R0903


class Template:
    def __init__(self, text: TextTree, styles: Styles, templates: TemplateStore):
        self.text = text
        self.styles = styles
        self.templates = templates
        self.props = Props()

    @property
    def html(self):
        return self._html(self.text)

    def _html(self, obj):
        if isinstance(obj, str):
            return obj
        text = ''.join([self._html(elt) for elt in obj])
        try:
            return self.get_text(obj, text)
        except AttributeError:
            return text

    def get_text(self, obj, text):
        name = obj.name
        style = self.styles[name]
        if style.template:
            template = obj[0]
            return self.templates[template].html
        return f'{style.start}{text}{style.end}'
