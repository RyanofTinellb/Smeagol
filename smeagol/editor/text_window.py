import tkinter as Tk

class TextWindow(Tk.Toplevel, object):

    """

    """
    def __init__(self, text='', font=None):
        super(TextWindow, self).__init__()
        self.font = font or ('Consolas', '14')
        self.top = self.winfo_toplevel()
        self.top.state('zoomed')
        textbox = Tk.Text(self, font=self.font)
        textbox.pack(side=Tk.LEFT, expand=True, fill=Tk.BOTH)
        textbox.insert(Tk.INSERT, text)
        textbox.config(state='disabled')
