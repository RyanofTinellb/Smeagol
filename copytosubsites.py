import shutil

paths = ['C:/Users/Ryan/Documents/TinellbianLanguages/grammar/',
            'C:/Users/Ryan/Documents/TinellbianLanguages/dictionary/']
src = 'C:/Users/Ryan/Documents/TinellbianLanguages/main/'
files = ['highlulani.ttf', '404search.js',
         'favicon.png', 'search.js', 'searchterms.js', 'basic_style.css']

for p in paths:
    for f in files:
        shutil.copy2(src + f, p)
