import os
import json
import socket
import tkinter.filedialog as fd
import webbrowser as web
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer as Server
from threading import Thread

from .defaults import default
from .utils import ignored

def save(obj, filename):
    try:
        saves(json.dumps(obj, ensure_ascii=False, indent=2), filename)
    except TypeError as e:
        saves(str(obj), f := f'{filename}!error.txt')
        raise TypeError(str(e), f)


def saves(string, filename):
    with ignored(os.error):
        os.makedirs(os.path.dirname(filename))
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(string)


def jsonify(obj):
    return json.dumps(obj, ensure_ascii=False)


def savelines(obj, filename):
    obj = ',\n'.join([jsonify(elt) for elt in obj])
    saves(f'[{obj}]', filename)


def load(filename):
    if not filename:
        return {}
    with open(filename, encoding='utf-8') as f:
        return json.load(f)

def loads(filename):
    if not filename:
        return ''
    with open(filename, encoding='utf-8') as f:
        return f.read()

def change(filename, fn, newfilename=None):
    '''Run function `fn` on entire object in filename'''
    newfilename = newfilename or filename
    obj = load(filename)
    fn(obj)
    save(obj, newfilename)


def update(filename, fn, newfilename=None):
    '''
    Run function `fn` on each element `elt` of an object `obj` in `filename`
    '''
    newfilename = newfilename or filename
    obj = load(filename)
    for elt in obj:
        fn(elt)
    save(obj, newfilename)


def updates(filename, fn, newfilename=None):
    newfilename = newfilename or filename
    saves(fn(loads(filename)), newfilename)


def open_source():
    options = dict(filetypes=[('Source Data File', '*.src')],
                   title='Open Source Data File',
                   defaultextension='.src')
    return fd.askopenfilename(**options)


def open_smeagol():
    options = dict(filetypes=[('Sméagol File', '*.smg'), ('Source Data File', '*.src')],
                   title='Open Site',
                   defaultextension='.smg')
    return fd.askopenfilename(**options)


def save_smeagol():
    options = dict(filetypes=[('Sméagol File', '*.smg')],
                   title='Save Site',
                   defaultextension='.smg')
    return fd.asksaveasfilename(**options)


def walk(root, condition):
    return [os.path.join(root, filename) for root, _, files in os.walk(root)
            for filename in files if condition(filename)]

def findbytype(root, ext):
    return walk(root, isfiletype(ext))

def find(root, name):
    return walk(root, lambda x: os.path.basename(x) == name)

def extension(filename):
    return os.path.splitext(filename)[1]

def isfiletype(ext):
    def _isfiletype(filename, ext=ext):
        return extension(filename) == ext
    return _isfiletype

def isfolder(filename):
    return os.path.isdir(filename)

servers = []


def start_server(port, directory=None, page404=''):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    page404 = page404 or default.page404
    while True:
        try:
            server = Server(("", port), Handler)
            servers.append(server)
            Handler.error_message_format = page404
            Thread(target=server.serve_forever).start()
            return port
        except socket.error:
            port += 1


def open_in_browser(port, link):
    web.open_new_tab(os.path.join(f'http://localhost:{port}', link))


def close_servers():
    for server in servers:
        server.shutdown()
