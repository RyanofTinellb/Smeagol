from smeagol import Dictionary
from cwsmeagol.editor.addremovelinks import (AddRemoveLinks,
                                             InternalDictionary, ExternalGrammar, Glossary)
from cwsmeagol.utils import remove_datestamp
import json
import re
from random import shuffle

output = []
transliteration = None
language = None
partofspeech = None
a = AddRemoveLinks([InternalDictionary(),
                    ExternalGrammar('c:/users/ryan/documents/tinellbianlanguages'
                                    '/dictionary/links.glk'),
                    Glossary('c:/users/ryan/documents/tinellbianlanguages'
                             '/grammar/glossary.gls')])
for entry in map(lambda entry: a.remove_links(remove_datestamp(entry.content)),
                 Dictionary()):
    for line in entry.splitlines():
        if line.startswith('[1]'):
            transliteration = line[len('[1]'):]
        elif line.startswith('[2]'):
            language = line[len('[2]'):]
        elif line.startswith('[5]'):
            line = re.sub(r'\[5\](.*?) <div class="definition">(.*?)</div>',
                          r'\1\n\2', line)
            newpos, meaning = line.splitlines()
            if newpos:
                partofspeech = re.sub(r'\(.*?\)', '', newpos).split(' ')
            definition = re.split(r'\W*', re.sub(r'<.*?>', '', meaning))
            output.append(dict(
                t=transliteration,
                l=language,
                p=partofspeech,
                d=definition,
                m=meaning
            ))
with open('c:/users/ryan/documents/tinellbianlanguages'
                '/dictionary/wordlist.json', 'w') as f:
    json.dump(output, f, indent=2)
