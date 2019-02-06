from sites import Grammar
import re
from smeagol.editor.addremovelinks import AddRemoveLinks
from smeagol.translation.markdown import Markdown

def geminate(regex):
    return re.sub(r'(&.*?;)\1', r'\1&#x2d0;', regex.group(0))

d = Grammar()
i = AddRemoveLinks(dict(
    ExternalDictionary="http://dictionary.tinellb.com"
))
m = Markdown('c:/users/ryan/documents/tinellbianlanguages/grammar/grammar.mkd')
for entry in d:
    old = i.remove_links(str(entry))
    text = re.sub(r'<ipa>.*?</ipa>', geminate, old)
    if old <> text:
        entry.text = i.add_links(text, entry)
        entry.publish(d.template)
        print entry.name
d.update_source()
