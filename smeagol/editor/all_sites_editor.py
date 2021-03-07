import os
from .editor import Editor

class AllSitesEditor(Editor):
    def __init__(self, master=None):
        super().__init__(master=master)
        self.open_all_sites('c:/users/ryan/tinellbianlanguages')
    
    def open_all_sites(self, root):
        files = [os.path.join(root, file_) for root, _, files in os.walk(root)
                 for file_ in files if file_.endswith('main.smg')]
        for i, site in enumerate(files):
            if i:
                self.new_tab()
            self.open_site(site)
