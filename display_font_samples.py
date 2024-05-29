import tkinter as tk
from tkinter import font

t = tk.Tk()
s = tk.Text(t)
s.pack(expand=True, fill=tk.BOTH)
s.config(font=font.Font(family='Times New Roman', size=15))
for f in sorted(font.families()):
    if not f.startswith('@'):
        tag = f.replace(' ', '')
        s.tag_config(tag, font=font.Font(family=f, size=40))
        s.insert(tk.END, f + '      ', )
        s.insert(tk.END, 'νv\n', tag)
t.mainloop()
