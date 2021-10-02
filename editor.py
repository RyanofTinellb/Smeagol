import os
import sys
from smeagol.editors import AllSites, Editor
from smeagol.utilities import errors, utils

utils.clear_screen()
try:
    filename = sys.argv[1]
except IndexError:
    filename = '-all'
if filename == '-all':
    AllSites().mainloop()
else:
    Editor(filename=filename).mainloop()
