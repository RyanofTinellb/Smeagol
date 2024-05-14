import json
import os
import random
import shutil
import socket
import tkinter.filedialog as fd
import webbrowser as web
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer as Server
from threading import Thread
from typing import Optional

import yaml
from smeagol.utilities.defaults import default
from smeagol.utilities.utils import ignored


def makedirs(filename):
    with ignored(os.error):
        os.makedirs(os.path.dirname(filename))


def save_json(obj, filename, indent=None):
    makedirs(filename)
    try:
        _save_json(obj, filename, indent)
    except TypeError as e:
        save_string(str(obj), f := f'{filename}!error.txt')
        raise TypeError(str(e), f) from e


def _save_json(obj, filename, indent=None):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)


def copy_all(files: dict):
    for src, dests in files.items():
        for dest in dests:
            shutil.copy(src, dest)


def save_string(string, filename):
    makedirs(filename)
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(string)


def save_yaml(obj, filename):
    makedirs(filename)
    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(obj, f, sort_keys=False, allow_unicode=True)


def jsonify(obj):
    return json.dumps(obj, ensure_ascii=False)


def savelines(obj, filename):
    obj = ',\n'.join([jsonify(elt) for elt in obj])
    save_string(f'[{obj}]', filename)


def load_json(filename):
    if not filename:
        return {}
    try:
        return _load_json(filename)
    except TypeError as e:
        raise TypeError(
            f'{filename} is not a json file, or is malformed') from e


def _load_json(filename):
    with open(filename, encoding='utf-8') as f:
        return json.load(f)


def load_string(filename):
    if not filename:
        return ''
    with open(filename, encoding='utf-8') as f:
        return f.read()


def load_yaml(filename, default_obj=None):
    if not filename:
        return default_obj or {}
    return _load_yaml(filename)


def _load_yaml(filename):
    with open(filename, encoding='utf-8') as f:
        return _safe_load_yaml(f, filename)


def _safe_load_yaml(file, filename):
    try:
        return yaml.safe_load(file)
    except (TypeError, AttributeError, ValueError) as e:
        raise type(e)(
            f'{filename} is not a yml file, or is malformed') from e


def change(filename, fn, newfilename=None):
    '''Run function `fn` on entire object in filename'''
    newfilename = newfilename or filename
    obj = load_yaml(filename)
    fn(obj)
    save_yaml(obj, newfilename)


def update(filename: str, fn: callable, newfilename: Optional[str] = None):
    '''
    Run function `fn` on each element `elt` of an object `obj` in `filename`
    '''
    newfilename = newfilename or filename
    obj = load_yaml(filename)
    for elt in obj:
        fn(elt)
    save_yaml(obj, newfilename)


def updates(filename, fn, newfilename=None):
    newfilename = newfilename or filename
    save_string(fn(load_string(filename)), newfilename)


def open_template():
    options = {'filetypes': [('Sméagol Template', '*.tpl')],
               'title': 'Open Sméagol Template',
               'defaultextension': '.tpl'}
    return load_yaml(fd.askopenfilename(**options))


def open_source():
    options = {'filetypes': [('Source Data File', '*.src')],
               'title': 'Open Source Data File',
               'defaultextension': '.src'}
    return fd.askopenfilename(**options)


def open_smeagol():
    options = {'filetypes': [('Sméagol File', '*.smg')],
               'title': 'Open Site',
               'defaultextension': '.smg'}
    return fd.askopenfilename(**options)


def save_smeagol():
    options = {'filetypes': [('Sméagol File', '*.smg')],
               'title': 'Save Site',
               'defaultextension': '.smg'}
    return fd.asksaveasfilename(**options)


def walk(root: str, condition: callable):
    return [os.path.join(root, filename) for root, _, files in os.walk(root)
            for filename in files if condition(filename)]


def find_by_type(root: str, ext: str):
    return walk(root, isfiletype(ext))


def find(root, name):
    return walk(root, lambda x: os.path.basename(x) == name)


def extension(filename):
    return os.path.splitext(filename)[1]


def isfiletype(ext):
    if not ext.startswith('.'):
        ext = '.' + ext

    def _isfiletype(filename, ext=ext):
        return extension(filename) == ext
    return _isfiletype


def isfolder(filename):
    return os.path.isdir(filename)


servers = []


def start_server(port=None, directory=None, page404=''):
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    page404 = page404 or default.page404
    port = port or random.randint(20000, 60000)
    while True:
        try:
            server = Server(('', port), Handler)
            servers.append(server)
            Handler.error_message_format = page404
            Thread(target=server.serve_forever).start()
            print(f'Serving {directory} on port {port}')
            return port, Handler
        except socket.error:
            port += 1


def open_in_browser(port, link=''):
    web.open_new_tab(os.path.join(f'http://localhost:{port}', link))


def close_servers():
    for server in servers:
        server.shutdown()
