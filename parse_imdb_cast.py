import re
import os
from smeagol.utilities import filesystem as fs


def parse(filename, result):
    k = reformat(fs.load_string(filename))
    # print(os.path.join('c:/users/ryan/desktop/imdb', os.path.basename(filename).replace('.html', '.yml')))
    # fs.save_yaml(k, os.path.join('c:/users/ryan/desktop/imdb', os.path.basename(filename).replace('.html', '.yml')))
    media = os.path.basename(filename).replace('.html', '')
    mode = None
    for line in k:
        if 'class="primary_photo"' in line:
            mode = 'photo'
        elif mode == 'photo' and line.startswith('a href='):
            nm = re.sub(r'a href="/name/(nm\d+).*', r'\1', line)
        elif mode == 'photo' and line.startswith('img '):
            name, pic = re.sub(r'img .*? title="(.*?)" src="(.*?)".*', r'\1>\2', line).split('>')
            actor = result.setdefault(nm, {'name': name, 'pic': pic})
            mode = None
        elif 'class="character"' in line:
            mode = 'character'
        elif mode == 'character' and not line.startswith('a href='):
            mode = None
            actor.setdefault('chars', []).append({'char': line, 'media': media})


def parse_television(filename, result):
    k = reformat(fs.load_string(filename))
    basename = os.path.basename(filename)
    media = basename.replace('.html', '')
    nm = ''
    pic = ''
    actor = {}
    mode = None
    for line in k:
        if line.startswith('a href='):
            nm = re.sub(r'a href="/name/(nm\d+)/.*', r'\1', line)
        elif line.startswith('img'):
            pic = re.sub(r'img src=".*" data-src-x2="(.*?)".*', r'\1', line)
        elif line == 'h4':
            mode = 'actor'
        elif mode == 'actor':
            actor = result.setdefault(nm, {'name': line, 'pic': pic})
            mode = None
        elif line == 'p class="h4 unbold"':
            mode = 'char'
        elif mode == 'char':
            char = re.sub(r'\(.*?\)', '', line)
            actor.setdefault('chars', []).append({'char': char, 'media': media})
            mode = None


def reformat(k):
    k = k.replace('\n', '').replace('&nbsp', ' ')
    k = re.sub(r'<tr class=".*?">', '<tr>', k)
    k = re.sub(r' +', ' ', k)
    k = re.split(r'[<>]', k)
    k = list(filter(reject, k))
    k = [str.strip(m) for m in k]
    return k


def reject(string):
    return not string in ('', ' ... ', ' ')


def main(root):
    filenames = fs.find_by_type(root, '.html')
    result = {}
    for filename in filenames:
        print(filename)
        fn = parse_television if '\\TV\\' in filename else parse
        fn(filename, result)
    print(len(result))
    fs.save_yaml(result, 'c:/users/ryan/onedrive/desktop/imdb cast.yml')
    dups = []
    for name in result.values():
        if len(name.get('chars', [])) > 1:
            sett = {}
            for char in name['chars']:
                sett.setdefault(char['char'], char['media'])
            if len(sett) > 1:
                dups.append([name['name'], sett])
    fs.save_yaml(dups, 'c:/users/ryan/onedrive/desktop/dups.yml')


ROOT = 'C:/Users/Ryan/OneDrive/Documents/IMDb'
main(ROOT)
