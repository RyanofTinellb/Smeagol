import sys
from smeagol.editors import AllSites, Editor
from smeagol.utilities import utils, filesystem as fs

utils.clear_screen()
try:
    filename = sys.argv[1]
except IndexError:
    AllSites().mainloop()
    exit()
if fs.isfolder(filename):
    filename = fs.findbytype(filename, '.smg')
Editor(filename=filename).mainloop()
