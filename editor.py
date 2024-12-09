'''
    $ editor.py
        opens a blank editor with an empty tab and the default interface
    $ editor.py c:/path/to/file.smg
        opens a particular site
    $ editor.py c:/path/to/directory
        opens every site within the directory
    $ editor.py c:/path/to/root directory-1 directory-2 ... directory-n
        opens every site with these directories
'''
import sys
import os

from smeagol.editor.api import Editor
from smeagol.utilities import filesystem as fs
from smeagol.utilities import utils


def main():
    utils.clear_screen()
    filenames = None
    with utils.ignored(IndexError):
        root = sys.argv[1]
        folders = [os.path.join(root, name) for name in sys.argv[2:]]
        filenames = [open_file(folder)[0] for folder in folders]
    Editor(filenames or open_file(root)).mainloop()


def open_file(path):
    if fs.isfolder(path):
        return fs.find_by_type(path, '.smg')
    return [path]


if __name__ == '__main__':
    main()
