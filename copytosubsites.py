import shutil

src = 'C:/Users/Ryan/TinellbianLanguages/toplevel/'


def copy(paths, files, src):
    for p in paths:
        for f in files:
            shutil.copy2(src + f, p)


paths = [
            'C:/Users/Ryan/TinellbianLanguages/coelacanth/',
            'C:/Users/Ryan/TinellbianLanguages/writings/',
			'C:/Users/Ryan/TinellbianLanguages/encyclopedia/',
            'C:/Users/Ryan/TinellbianLanguages/grammar/',
        ]
files =  ['404search.js', 'search.js']

copy(paths, files, src)

paths += [
            'C:/Users/Ryan/TinellbianLanguages/dictionary/'
         ]

files = ['tinellb.ttf', 'favicon.png', 'searchterms.js', 'basic_style.css']

copy(paths, files, src)
