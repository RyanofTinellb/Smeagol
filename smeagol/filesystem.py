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
    except TypeError:
        saves(str(obj), f := filename + '!error.txt')
        print(f)
        raise


def saves(string, filename):
    with ignored(os.error):
        os.makedirs(os.path.dirname(filename))
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(string)


def load(filename):
    with open(filename, encoding='utf-8') as f:
        return json.load(f)


def loads(filename):
    with open(filename, encoding='utf-8') as f:
        return f.read()


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
    return [os.path.join(root, file_) for root, _, files in os.walk(root)
            for file_ in files if condition(file_)]


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
