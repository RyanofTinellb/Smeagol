from tkinter import Text

START = "1.0"
END = "end-1c"
INSERT = "insert"


class BaseTextbox(Text):

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs)
        return self

    def add_commands(self, commands):
        for keys, command in commands:
            if isinstance(keys, str):
                self.bind(keys, command)
            else:
                for key in keys:
                    self.bind(key, command)

    def bind(self, key, command):
        if key == '<<FollowLink>>':
            self._link_follower = command
            return
        super().bind(key, command)

    @property
    def formatted_text(self):
        return self.formatted_get()

    def read(self, start=START, end=END):
        return super().get(start, end)

    def get_char(self, position=INSERT):
        return super().get(position)

    def formatted_get(self, start=START, end=END):
        return [t for t in super().dump(start, end)
                if t[1] != 'sel' and t[0] != 'mark']
