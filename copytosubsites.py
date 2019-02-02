import shutil

src = 'C:/Users/Ryan/Documents/TinellbianLanguages/main/'


def copy(paths, files, src):
    for p in paths:
        for f in files:
            shutil.copy2(src + f, p)


paths = [
            'C:/Users/Ryan/Documents/TinellbianLanguages/coelacanth/',
            'C:/Users/Ryan/Documents/TinellbianLanguages/writings/',
			'C:/Users/Ryan/Documents/TinellbianLanguages/encyclopedia/',
            'C:/Users/Ryan/Documents/TinellbianLanguages/grammar/',
        ]
files =  ['404search.js', 'search.js']

copy(paths, files, src)

paths += [
            'C:/Users/Ryan/Documents/TinellbianLanguages/dictionary/'
         ]

files = ['highlulani.ttf', 'favicon.png', 'searchterms.js', 'basic_style.css']

copy(paths, files, src)
