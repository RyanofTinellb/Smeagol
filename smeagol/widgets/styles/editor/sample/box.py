from tkinter.font import Font
import tkinter as tk

class Box(tk.Text):
    def __init__(self, parent, style):
        super().__init__(parent, height=5, width=30)
        font = Font(self, **style._font)
        self.tag_configure('default', font=font, **style.paragraph)
        self.config(font='Calibri 18', wrap='word')
        lorem = ('Lorem ipsum dolor sit amet, consectetur adipiscing elit, '
                    'sed do eiusmod tempor incididunt ut labore et dolore '
                    'magna aliqua. Ut enim ad minim veniam, quis nostrud '
                    'exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.')
        self.insert(1.0, lorem, 'default')