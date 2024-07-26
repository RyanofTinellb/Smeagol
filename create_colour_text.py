# pylint: disable=C0103, W0611, C0305, C0304, C0301
import tkinter as tk

from smeagol.api import filesystem as fs

a = ['0', '3', '6', '9', 'c', 'f']
# t = tk.Tk()
f = tk.Text()
f.grid()

for r in a:
    for g in a:
        for b in a:
            t = r+g+b
            f.config(font=tk.font.Font(family="Courier New", size=18))
            f.tag_config(t, background=f'#{t}')
            f.insert('insert', t, t)
            f.insert('insert', ' ')
        f.insert('insert', '   ')
    f.insert('insert', '\n')

f.mainloop()
