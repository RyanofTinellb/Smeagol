import os
from .. import filesystem as fs
from .editor import Editor

class AllSitesEditor(Editor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.open_all_sites('c:/users/ryan/tinellbianlanguages')
    
    @staticmethod
    def _smg(filename):
        return filename.endswith('.smg')
    
    def open_all_sites(self, root):
        files = fs.walk(root, self._smg)
        for i, site in enumerate(files):
            if i:
                self.new_tab()
            self.open_site(site)
