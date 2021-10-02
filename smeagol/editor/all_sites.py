from ..utilities import filesystem as fs
from .editor import Editor

class AllSites(Editor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.open_all_sites('c:/users/ryan/tinellbianlanguages')
    
    def open_all_sites(self, root):
        for i, site in enumerate(fs.findbytype(root, '.smg')):
            if i:
                self.new_tab()
            self.open_site(site)
