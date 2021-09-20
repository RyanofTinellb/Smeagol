import os
import sys
from smeagol import AllSitesEditor, Editor, utils, errors

utils.clear_screen()
try:
    filename = sys.argv[1]
except IndexError:
    filename = '-all'
if filename == '-all':
    AllSitesEditor().mainloop()
else:
    Editor(filename=filename).mainloop()