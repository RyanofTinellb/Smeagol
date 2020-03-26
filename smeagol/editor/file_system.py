import tkinter.filedialog as fd

def open_smeagol():
    options = dict(filetypes=[('Sméagol File', '*.smg'), ('Source Data File', '*.src')],
                    title='Open Site',
                    defaultextension='.smg')
    return fd.askopenfilename(**options)