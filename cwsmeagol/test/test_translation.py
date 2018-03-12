import unittest
from translation import *
from smeagol import *
from site_editor import *

def testExternalDictionaryAddLinks():
    grammar = Grammar()
    nouns = grammar['Nouns']
    links = ExternalDictionary()
    markdown = Markdown('c:/users/ryan/documents/tinellbianlanguages/grammarstoryreplacements.mkd')
    text = """==={Ra'ani} ((Ryan)) (name of a person)
=={''ikinnisa} ((Eakins)) (name of a family)
==[[Sa'imi]] ((Caemi)) (name of a deity)
==[[Tinalli]] ((Tinellb)) (name of a universe)
==[[''irri'a]] ((Ir&igrave;a)) (name of a city)
==[[Lulani]] ((Lulani)) (name of a language)
==[[Xuci]][[pura]] [[Cula]] ((The Crackled Egg)) (name of a story)"""
    text = markdown.to_markup(text)
    text = links.add_links(text, nouns, grammar)
    text = add_datestamp(text)
    print(text)

def testUrlFormWithMarkdown():
    site = Grammar()
    link = "&#x294;irri'a"
    url = urlform(link, site.markdown)
    print(url)

if __name__ == '__main__':
    testUrlFormWithMarkdown()
