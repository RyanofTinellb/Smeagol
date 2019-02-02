from sites import Dictionary
import re
from smeagol.editor.addremovelinks import AddRemoveLinks
from smeagol.translation.markdown import Markdown

d = Dictionary()
i = AddRemoveLinks(dict(
    ExternalGrammar="C:/Users/Ryan/Documents/TinellbianLanguages/dictionary/links.glk"
))
m = Markdown('c:/users/ryan/documents/tinellbianlanguages/dictionary/dictionary.mkd')
for entry in d:
    old = str(entry)
    text = old.replace('\n', '&para;')
    text = text.replace('[/d][d pronunciation]', '[/d]&para;[d pronunciation]')
    text = text.replace('&para;', '\n')
    if old <> text:
        entry.text = text
        entry.publish(d.template)
        print entry.name
d.update_source()
