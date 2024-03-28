'''
    $ editor.py
        opens a blank editor with an empty tab and the default interface
    $ editor.py c:/path/to/file.smg
        opens a particular site
    $ editor.py c:/path/to/directory
        opens every site within the directory
'''
import sys

from smeagol.editor.api import Editor
from smeagol.utilities import filesystem as fs
from smeagol.utilities import utils


def main():
    utils.clear_screen()
    try:
        path = sys.argv[1]
        filenames = get_filenames(path)
    except IndexError:  # no command line arguments
        filenames = []
    Editor(filenames=filenames).mainloop()

def other():
    utils.clear_screen()
    path = 'c:/users/ryan/tinellbianlanguages/encyclopedia'
    filenames = get_filenames(path)
    Editor(filenames=filenames).mainloop()


def get_filenames(path):
    if fs.isfolder(path):
        return fs.find_by_type(path, '.smg')
    return [path]


if __name__ == '__main__':
    # main()
    other()
