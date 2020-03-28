import tkinter.filedialog as fd

def open_smeagol():
    options = dict(filetypes=[('Sméagol File', '*.smg'), ('Source Data File', '*.src')],
                    title='Open Site',
                    defaultextension='.smg')
    return fd.askopenfilename(**options)

def save_smeagol():
    options = dict(filetypes=[('Sméagol File', '*.smg')],
                    title='Save Site',
                    defaultextension='.smg')
    return fd.asksaveasfilename(**options)