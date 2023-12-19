import tkinter as tk


class StyledTextbox(tk.Text):
    def __init__(self, parent=None):
        super().__init__(parent, height=1, width=1, wrap=tk.WORD, undo=True)
        self.displays = {"style": tk.StringVar(),
                         "language": tk.StringVar()}

    def clear_style(self, styles):
        self.tag_remove(styles, tk.INSERT)

    def set_styles(self):
        if self.styles is None:
            return
        with utils.ignored(KeyError):
            self.set_default_style()
        for style in self.styles:
            self._set_style(style)

    def set_default_style(self):
        if default := self.styles.default:
            self.config(**default.textbox_settings)

    def _set_style(self, style):
        name = style.name
        key = style.key
        self.tag_config(name, **style.paragraph)
        if style.language:
            for language in self.languages:
                language = language[:2]
                self.tag_config(f"{name}-{language}", **style.paragraph)
        if key:
            self.bind(f"<Control-{key}>", self.style_changer(name, style))

    def style_changer(self, name, style):
        def command(_=None, name=name):
            if style.language and (code := self.language_code):
                name += f"-{code}"
            self.styles.toggle(name)
            return "break"

        return command

    def _add_style(self, name):
        self.styles.activate(name)
        with utils.ignored(tk.TclError):
            self.tag_add(name, *SELECTION)

    def _remove_style(self, name):
        self.styles.deactivate(name)
        with utils.ignored(tk.TclError):
            self.tag_remove(name, *SELECTION)

    def update_styles(self):
        self.set_styles()
        self.add_commands()
