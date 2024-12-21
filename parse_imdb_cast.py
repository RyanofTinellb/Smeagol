import re
import os
from smeagol.utilities import filesystem as fs


def parse(filename, result):
    k = reformat(fs.load_string(filename))
    # fs.save_yaml(k, os.path.join('c:/users/ryan/desktop/imdb', os.path.basename(filename)))
    link = ''
    mode = None
    maindict = {}
    for n in k:
        if n == 'tr':
            subdict = {'media': os.path.basename(filename)[:-5]}
        elif n == '/tr':
            try:
                subdict['char'] = ' / '.join(subdict['char'])
                maindict.setdefault('chars', []).append(subdict)
            except KeyError:
                pass
            mode = None
        elif n.startswith('td'):
            mode = re.sub(r'td class="(.*?)"', r'\1', n)
        elif n.startswith('img '):
            maindict = result.setdefault(link, {})
            maindict['name'], maindict['pic'] = re.sub(
                r'.*?title="(.*?)" src="(.*?)".*', r'\1>\2', n).split('>')
        elif (mode == "character" and n and not n.startswith('/')
                and not n.startswith('(') and not n.startswith('a href')):
            subdict.setdefault('char', []).append(n)
        elif mode == 'primary_photo' and n.startswith('a href='):
            link = re.sub(r'a href="(.*?)(\?.*?)*".*', r'\1', n)

def parse_television(filename, result):
    k = reformat(fs.load_string(filename))
    print(k)
    fs.save_yaml(k, os.path.join('c:/users/ryan/desktop/imdb', os.path.basename(filename)))
    return k, result

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
    print('running')
    filenames = fs.find_by_type(root, '.html')
    result = {}
    for filename in filenames:
        fn = parse_television if os.path.basename(filename).startswith('TV ') else parse
        fn(filename, result)
    fs.save_yaml(result, 'c:/users/ryan/desktop/imdb cast.yml')
    dups = ''
    for name in result.values():
        if len(name.get('chars', [])) > 1:
            sett = {}
            for char in name['chars']:
                sett.setdefault(char['char'], char['media'])
            if len(sett) > 1:
                dups += name['name'] + '\n'
                for (char, media) in sett.items():
                    dups += 2 * ' ' + char + ' - ' + media + '\n'
    fs.save_string(dups, 'c:/users/ryan/desktop/dups.txt')


ROOT = 'C:/Users/Ryan/OneDrive/Documents/IMDb'
# filename = 'C:/Users/Ryan/OneDrive/Documents/useful/films.txt'
# for i, line in enumerate(fs.readlines(filename)):
#     print(str(9 - i) + '. ', line)
#     fs.save_string('', os.path.join(root, line + '.html'))
#     os.startfile(os.path.join(root, line + '.html'))
#     fs.open_in_browser(None, 'https://www.imdb.com/find/?q=' + line, False)
#     main()
#     input('?> ')
main(ROOT)
