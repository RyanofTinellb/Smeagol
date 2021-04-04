import os
import sys
from smeagol import AllSitesEditor, Editor, utils

utils.clear_screen()
try:
    filename = sys.argv[1]
except IndexError:
    filename = None
if filename == '-all':
    AllSitesEditor().mainloop()
else:
    Editor(filename=filename).mainloop()