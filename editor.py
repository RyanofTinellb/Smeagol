import sys
from smeagol.editor.api import Editor
from smeagol.utilities import utils, filesystem as fs

'''
    $ editor.py
        opens a blank editor with an empty tab and the default interface
    $ editor.py c:/path/to/file.smg
        opens a particular site
    $ editor.py c:/path/to/directory
        opens every site within the directory
'''
def main():
    utils.clear_screen()
    try:
        path = sys.argv[1]
        filenames = get_filenames(path)
    except IndexError:  # no command line arguments
        filenames = []
    Editor(filenames=filenames).mainloop()


def get_filenames(path):
    if fs.isfolder(path):
        return fs.findbytype(path, '.smg')
    return [path]

if __name__ == '__main__':
    main()