# Conlang Website Creation
This repository holds a suite of Python programs which take a number of text files and transforms them into HTML. These programs are optimised for creating and editing dictionaries in multiple constructed languages (conlangs), and for translating a novel paragraph by paragraph.

*Smeagol.py* - A pun on GitHub's Jekyll (both are characters with darker dissociative identities), Sméagol converts semi-markdown text into HTML markup.

*Translation.py* - a utility module containing the following classes:
+ Translator:
If you have made a specific font for your conlang, this can transform a transliteration scheme into script. In conjunction with Sméagol, CSS and FontCreator (or similar), you end up with something that looks like the script on [this page](http://dictionary.tinellb.com/k/kicu.html). The Translator can be customised with additional languages.
```python
>>> from Translation import Translator
>>> translator = Translator('hl') # choose High Lulani
>>> print(translator.convert_word('kicu'))
'[hl]\(Ky\)[/hl]'
```
+ RandomWords:
This yields a list of random words. This can be customised to follow your own phonotactics.
```python
>>> from Translation import RandomWords
>>> words = RandomWords(5)
>>> for x in words:
... print(x)
'duri'
'majuci'
'dixa'
'haritu'
'dijufa'
```
+ Markdown:
This converts text to and from markdown, based on a given textfile. If the second argument is True, this will also append (on markup) or delete (on markdown) a timestamp.
```python
>>> from Translation import Markdown
>>> marker = Markdown('c:/users/documents/replacements.txt')
>>> markdown = marker.to_markdown()
>>> markup = marker.to_markup()
>>> print(markdown('<em> &copy; &aacute; </em> &date=20170716'), False)
'[b] (c) )a [/b]'
>>> print(markup('[b] (c) )a [/b]'), True)
'<em> &copy; &aacute; </em> &date=20170716'
```
*EditGrammarStory.py* - opens a GUI to allow for editing pages in markdown.

*EditDictionary.py* - opens a GUI to allow for adding and modifying dictionary entries, catalogued and ordered. Select your language, input a headword into the textbox and press 'Return' on the keyboard. Press "Publish" to save to the datafile and create/modify the entry page and its alphabetical category page. Leave the edit area blank to delete that page.

Keyboard shortcuts include:
+ Ctrl+S: Save/Publish
+ Ctrl+R: Refresh random words
+ Alt-D: Go to headword box
+ Ctrl-N: Insert new word template
+ Ctrl-A: Select all
+ Ctrl-Z: Undo
+ Ctrl-Y: Redo
+ Ctrl-B: Bold
+ Ctrl-I: Italic
+ Ctrl-K: Small capitals
+ Ctrl-=: Insert definition area
+ Ctrl-T: Translate a selected word, using the Translator
+ Ctrl-Backspace: Delete one word backwards when typing
```python
>>> from EditDictionary import EditDictionary
>>> directory = 'c:/users/documents/website'
>>> lexicon = Site('Conlang Dictionary', 3, dir)
>>> app = EditDictionary(dir=directory,               # directory where the site is kept
                    outputfile='data.txt',            # the location of the raw datafile
                    site=lexicon,                     # a Site instance
                    markdown='../replacements.html',  # the location of the markdown file
                    searchfile='searching.json',      # the location of the new searchfile database
                    randomwords=20)                   # the number of random words to appear together
>>> app.master.title('Edit the Lexicon')
>>> app.mainloop()
```

*TranslateStory.py* - opens a GUI to allow for simultaneous editing of original language, transliteration, and gloss/literal. These also act as inputs to create an interlinear, and the conlang in its script.
