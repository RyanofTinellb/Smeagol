from tkinter import Text

START = "1.0"
END = "end-1c"
INSERT = "insert"


class BaseTextbox(Text):

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs)
        return self

    @property
    def formatted_text(self):
        return self.formatted_get()

    def read(self, start=START, end=END):
        return super().get(start, end)

    def get_char(self, position=INSERT):
        return super().get(position)

    def formatted_get(self, start=START, end=END):
        return super().dump(start, end)
